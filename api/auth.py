"""
Module d'authentification pour l'API de recommandation de films.
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Request
import psycopg2
from config.database import get_connection_dict

# Durée de vie des sessions (30 jours)
SESSION_DURATION_DAYS = 30


def hash_password(password: str) -> str:
    """Hash un mot de passe avec SHA-256 et un salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    try:
        salt, stored_hash = password_hash.split(":")
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == stored_hash
    except:
        return False


def generate_session_token() -> str:
    """Génère un token de session unique."""
    return secrets.token_urlsafe(32)


def get_avatar_url(gender: Optional[str] = None) -> str:
    """Génère une URL d'avatar basée sur le genre."""
    if gender == "femme":
        return "https://api.dicebear.com/7.x/avataaars/svg?seed=femme&backgroundColor=b6e3f4,c0aede,d1d4f9"
    elif gender == "homme":
        return "https://api.dicebear.com/7.x/avataaars/svg?seed=homme&backgroundColor=b6e3f4,c0aede,d1d4f9"
    else:
        return "https://api.dicebear.com/7.x/avataaars/svg?seed=default&backgroundColor=b6e3f4,c0aede,d1d4f9"


async def get_current_user(request: Request) -> Optional[Dict]:
    """Récupère l'utilisateur actuel depuis la session."""
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        cur.execute("""
            SELECT u.id, u.username, u.email, u.role, u.gender, u.avatar_url, 
                   u.is_active, u.is_blocked, u.restrictions
            FROM users u
            JOIN user_sessions s ON s.user_id = u.id
            WHERE s.session_token = %s 
              AND s.is_active = TRUE 
              AND s.expires_at > NOW()
              AND u.is_active = TRUE
              AND u.is_blocked = FALSE
        """, (session_token,))
        
        user = cur.fetchone()
        if user:
            return dict(user)
        return None
    except Exception as e:
        return None
    finally:
        if conn:
            conn.close()


async def require_auth(request: Request) -> Dict:
    """Exige que l'utilisateur soit authentifié."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentification requise")
    return user


async def require_admin(request: Request) -> Dict:
    """Exige que l'utilisateur soit admin."""
    user = await require_auth(request)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès admin requis")
    return user


def create_session(user_id: int, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> str:
    """Crée une nouvelle session pour un utilisateur."""
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(days=SESSION_DURATION_DAYS)
        
        cur.execute("""
            INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, expires_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, session_token, ip_address, user_agent, expires_at))
        
        conn.commit()
        return session_token
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la session: {str(e)}")
    finally:
        if conn:
            conn.close()


def delete_session(session_token: str):
    """Supprime une session."""
    conn = None
    try:
        conn, cur = get_connection_dict()
        cur.execute("UPDATE user_sessions SET is_active = FALSE WHERE session_token = %s", (session_token,))
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

