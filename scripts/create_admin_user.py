"""
Script pour créer un utilisateur administrateur.
Usage: python scripts/create_admin_user.py
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_connection_dict
from api.auth import hash_password, get_avatar_url
import getpass

def create_admin_user():
    """Crée un utilisateur administrateur."""
    print("=== Création d'un utilisateur administrateur ===\n")
    
    username = input("Nom d'utilisateur: ").strip()
    if not username:
        print("Erreur: Le nom d'utilisateur est requis")
        return
    
    email = input("Email: ").strip()
    if not email or "@" not in email:
        print("Erreur: Un email valide est requis")
        return
    
    password = getpass.getpass("Mot de passe: ")
    if len(password) < 6:
        print("Erreur: Le mot de passe doit contenir au moins 6 caractères")
        return
    
    password_confirm = getpass.getpass("Confirmer le mot de passe: ")
    if password != password_confirm:
        print("Erreur: Les mots de passe ne correspondent pas")
        return
    
    gender = input("Genre (homme/femme/autre, optionnel): ").strip().lower()
    if gender and gender not in ["homme", "femme", "autre"]:
        gender = None
    
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        # Vérifier si l'utilisateur existe déjà
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            print("Erreur: Un utilisateur avec ce nom d'utilisateur ou cet email existe déjà")
            return
        
        # Créer l'utilisateur admin
        password_hash = hash_password(password)
        avatar_url = get_avatar_url(gender if gender else None)
        
        cur.execute("""
            INSERT INTO users (username, email, password_hash, gender, avatar_url, role)
            VALUES (%s, %s, %s, %s, %s, 'admin')
            RETURNING id, username, email, role
        """, (username, email, password_hash, gender, avatar_url))
        
        user = cur.fetchone()
        conn.commit()
        
        print(f"\n✅ Utilisateur administrateur créé avec succès!")
        print(f"   ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Rôle: {user['role']}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erreur lors de la création de l'utilisateur: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_admin_user()

