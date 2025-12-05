"""
API FastAPI pour les recommandations de films avec pgvector.
Rôle 3: API et intégration
"""
from fastapi import FastAPI, HTTPException, Query, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
import os
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_connection, get_connection_dict, close_connection_pool
from dotenv import load_dotenv
import psycopg2
from api.auth import (
    hash_password, verify_password, create_session, delete_session,
    get_current_user, require_auth, require_admin, get_avatar_url
)
from api.tmdb_service import get_film_metadata, get_movie_poster_url, get_movie_trailer, get_streaming_platforms

# Import lazy de SentenceTransformer pour éviter les problèmes au démarrage
SentenceTransformer = None

load_dotenv()

app = FastAPI(
    title="API de Recommandation de Films",
    description="API de recherche sémantique et recommandation de films utilisant pgvector",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement du modèle d'embeddings (une seule fois au démarrage)
_model = None
_model_loading_error = None

def get_model():
    """Retourne le modèle d'embeddings (chargé en lazy loading avec optimisation mémoire)."""
    global _model, _model_loading_error, SentenceTransformer
    
    if _model_loading_error:
        raise _model_loading_error
    
    # Import lazy de SentenceTransformer
    if SentenceTransformer is None:
        try:
            from sentence_transformers import SentenceTransformer as ST
            SentenceTransformer = ST
        except OSError as e:
            if "1114" in str(e) or "dll" in str(e).lower():
                error_msg = (
                    "Erreur lors du chargement de PyTorch. "
                    "Réinstallez PyTorch avec: pip install torch --force-reinstall"
                )
                _model_loading_error = HTTPException(status_code=503, detail=error_msg)
                raise _model_loading_error
            else:
                raise
    
    if _model is None:
        try:
            model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
            print(f"Chargement du modèle: {model_name}")
            
            # Options pour réduire l'utilisation mémoire
            # Utiliser device='cpu' pour éviter les problèmes de GPU
            # et réduire la consommation mémoire
            try:
                import torch
                device = 'cpu'
            except:
                device = 'cpu'
            
            # Charger le modèle avec des options optimisées
            _model = SentenceTransformer(
                model_name,
                device=device,
            )
            
            # Mettre le modèle en mode évaluation pour économiser la mémoire
            _model.eval()
            
            # Optionnel: désactiver le gradient pour économiser la mémoire
            try:
                for param in _model.parameters():
                    param.requires_grad = False
            except:
                pass  # Ignorer si pas de paramètres
                
            print(f"Modèle chargé avec succès sur {device}")
            
        except OSError as e:
            if "1455" in str(e) or "paging file" in str(e).lower() or "fichier de pagination" in str(e).lower():
                error_msg = (
                    "Erreur de mémoire insuffisante lors du chargement du modèle. "
                    "Solutions: augmentez le fichier de pagination Windows, "
                    "utilisez un modèle plus léger (all-MiniLM-L6-v2), "
                    "ou fermez d'autres applications."
                )
                _model_loading_error = HTTPException(status_code=503, detail=error_msg)
                raise _model_loading_error
            else:
                _model_loading_error = HTTPException(
                    status_code=500,
                    detail=f"Erreur lors du chargement du modèle: {str(e)}"
                )
                raise _model_loading_error
        except Exception as e:
            _model_loading_error = HTTPException(
                status_code=500,
                detail=f"Erreur lors du chargement du modèle: {str(e)}"
            )
            raise _model_loading_error
    
    return _model


# Modèles Pydantic pour les réponses
class Film(BaseModel):
    id: int
    title: str
    year: Optional[int] = None
    genres: Optional[List[str]] = None
    cast: Optional[List[str]] = None
    synopsis: Optional[str] = None
    meta: Optional[dict] = None


class Recommendation(BaseModel):
    film: Film
    distance: float = Field(..., description="Distance de similarité (plus petit = plus similaire)")


class RecommendationResponse(BaseModel):
    query_film_id: Optional[int] = None
    query_text: Optional[str] = None
    recommendations: List[Recommendation]
    count: int


# Modèles pour l'authentification
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    gender: Optional[str] = Field(None, pattern="^(homme|femme|autre)$")


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    gender: Optional[str]
    avatar_url: Optional[str]


# Servir les fichiers statiques
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.on_event("shutdown")
async def shutdown_event():
    """Ferme les connexions à la base de données lors de l'arrêt."""
    close_connection_pool()


@app.get("/app", tags=["Web Interface"])
async def web_interface():
    """Serve l'interface web de l'application."""
    static_path = Path(__file__).parent.parent / "static" / "index.html"
    if static_path.exists():
        return FileResponse(str(static_path))
    else:
        raise HTTPException(status_code=404, detail="Interface web non trouvée")


@app.get("/login", tags=["Web Interface"])
async def login_page():
    """Serve la page de connexion."""
    static_path = Path(__file__).parent.parent / "static" / "login.html"
    if static_path.exists():
        return FileResponse(str(static_path))
    else:
        raise HTTPException(status_code=404, detail="Page de connexion non trouvée")


@app.get("/admin", tags=["Web Interface"])
async def admin_page():
    """Serve la page admin."""
    static_path = Path(__file__).parent.parent / "static" / "admin.html"
    if static_path.exists():
        return FileResponse(str(static_path))
    else:
        raise HTTPException(status_code=404, detail="Page admin non trouvée")


@app.get("/", tags=["Web Interface"])
async def root():
    """Route racine - redirige vers l'interface web ou l'API info."""
    static_path = Path(__file__).parent.parent / "static" / "index.html"
    if static_path.exists():
        return FileResponse(str(static_path))
    else:
        # Fallback vers l'API JSON si l'interface n'existe pas
        return {
            "message": "API de Recommandation de Films",
            "version": "1.0.0",
            "description": "API de recherche sémantique et recommandation de films utilisant pgvector",
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json"
            },
            "links": {
                "swagger_docs": "/docs",
                "redoc_docs": "/redoc"
            }
        }


@app.get("/login", tags=["Web Interface"])
async def login_page():
    """Page de connexion."""
    static_path = Path(__file__).parent.parent / "static" / "login.html"
    if static_path.exists():
        return FileResponse(str(static_path))
    else:
        raise HTTPException(status_code=404, detail="Page de connexion non trouvée")


@app.get("/admin", tags=["Web Interface"])
async def admin_page():
    """Page d'administration."""
    static_path = Path(__file__).parent.parent / "static" / "admin.html"
    if static_path.exists():
        return FileResponse(str(static_path))
    else:
        raise HTTPException(status_code=404, detail="Page admin non trouvée")


@app.get("/api/info", tags=["Info"])
def api_info():
    """Endpoint de base pour vérifier que l'API fonctionne."""
    return {
        "message": "API de Recommandation de Films",
        "version": "1.0.0",
        "description": "API de recherche sémantique et recommandation de films utilisant pgvector",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "recommend_by_film": {
                "path": "/recommend/by-film/{film_id}",
                "description": "Recommandations basées sur un film",
                "method": "GET",
                "example": "/recommend/by-film/1?k=10"
            },
            "search": {
                "path": "/search",
                "description": "Recherche sémantique de films",
                "method": "GET",
                "example": "/search?q=sci-fi space&k=10"
            },
            "film_details": {
                "path": "/films/{film_id}",
                "description": "Détails d'un film",
                "method": "GET",
                "example": "/films/1"
            },
            "stats": {
                "path": "/stats",
                "description": "Statistiques de la base de données",
                "method": "GET",
                "example": "/stats"
            }
        },
        "links": {
            "swagger_docs": "/docs",
            "redoc_docs": "/redoc"
        }
    }


@app.get("/recommend/by-film/{film_id}", response_model=RecommendationResponse, tags=["Recommandation"])
def recommend_by_film(
    film_id: int,
    k: int = Query(10, ge=1, le=100, description="Nombre de recommandations"),
    exclude_genres: Optional[str] = Query(None, description="Genres à exclure, séparés par des virgules"),
    min_year: Optional[int] = Query(None, description="Année minimum"),
    max_year: Optional[int] = Query(None, description="Année maximum")
):
    """
    Recommande des films similaires à un film donné.
    
    Utilise la similarité cosinus sur les embeddings pour trouver les films les plus proches.
    """
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        # Vérifier que le film existe
        cur.execute("SELECT id, title FROM films WHERE id = %s", (film_id,))
        film_check = cur.fetchone()
        if not film_check:
            raise HTTPException(status_code=404, detail=f"Film avec l'id {film_id} non trouvé")
        
        # Construire la requête avec filtres optionnels
        filters = []
        filter_params = []
        
        if exclude_genres:
            genres_to_exclude = [g.strip() for g in exclude_genres.split(",")]
            for genre in genres_to_exclude:
                filters.append("NOT (%s = ANY(f.genres))")
                filter_params.append(genre)
        
        if min_year:
            filters.append("f.year >= %s")
            filter_params.append(min_year)
        
        if max_year:
            filters.append("f.year <= %s")
            filter_params.append(max_year)
        
        filter_clause = " AND " + " AND ".join(filters) if filters else ""
        
        # Ordre des paramètres : film_id (WITH), film_id (WHERE), filtres, k (LIMIT)
        params = [film_id, film_id] + filter_params + [k]
        
        query = f"""
        WITH q AS (
            SELECT embedding FROM film_embeddings WHERE film_id = %s
        )
        SELECT 
            f.id, f.title, f.year, f.genres, f."cast", f.synopsis, f.meta,
            (fe.embedding <=> (SELECT embedding FROM q)) AS distance
        FROM film_embeddings fe
        JOIN films f ON f.id = fe.film_id
        JOIN q ON TRUE
        WHERE f.id <> %s
        {filter_clause}
        ORDER BY fe.embedding <=> (SELECT embedding FROM q)
        LIMIT %s
        """
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        recommendations = []
        for row in results:
            recommendations.append(
                Recommendation(
                    film=Film(
                        id=row["id"],
                        title=row["title"],
                        year=row["year"],
                        genres=row["genres"],
                        cast=row["cast"],
                        synopsis=row["synopsis"],
                        meta=row["meta"]
                    ),
                    distance=float(row["distance"])
                )
            )
        
        return RecommendationResponse(
            query_film_id=film_id,
            recommendations=recommendations,
            count=len(recommendations)
        )
        
    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        error_msg = str(e).replace('\n', ' ')
        raise HTTPException(
            status_code=503,
            detail=f"Erreur de connexion à PostgreSQL: {error_msg}"
        )
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recommandation: {error_msg}"
        )
    finally:
        if conn:
            conn.close()


@app.get("/search", response_model=RecommendationResponse, tags=["Recherche"])
async def search(
    q: str = Query(..., description="Requête textuelle de recherche"),
    k: int = Query(10, ge=1, le=100, description="Nombre de résultats"),
    genres: Optional[str] = Query(None, description="Genres requis, séparés par des virgules"),
    min_year: Optional[int] = Query(None, description="Année minimum"),
    max_year: Optional[int] = Query(None, description="Année maximum"),
    request: Request = None
):
    """
    Recherche sémantique de films à partir d'une requête textuelle.
    
    La requête est convertie en embedding et comparée avec les embeddings des films.
    """
    conn = None
    try:
        # Générer l'embedding de la requête
        model = get_model()
        query_embedding = model.encode([q], normalize_embeddings=True)[0]
        vec_str = "[" + ",".join(f"{x:.8f}" for x in query_embedding.tolist()) + "]"
        
        conn, cur = get_connection_dict()
        
        # Construire la requête avec filtres
        filters = []
        filter_params = []
        
        if genres:
            genres_list = [g.strip() for g in genres.split(",")]
            for genre in genres_list:
                filters.append("%s = ANY(f.genres)")
                filter_params.append(genre)
        
        if min_year:
            filters.append("f.year >= %s")
            filter_params.append(min_year)
        
        if max_year:
            filters.append("f.year <= %s")
            filter_params.append(max_year)
        
        filter_clause = " AND " + " AND ".join(filters) if filters else ""
        
        # Ordre des paramètres : vec_str (SELECT), filtres, vec_str (ORDER BY), k (LIMIT)
        params = [vec_str] + filter_params + [vec_str, k]
        
        query = f"""
        SELECT 
            f.id, f.title, f.year, f.genres, f."cast", f.synopsis, f.meta,
            (fe.embedding <=> %s::vector) AS distance
        FROM film_embeddings fe
        JOIN films f ON f.id = fe.film_id
        WHERE 1=1
        {filter_clause}
        ORDER BY fe.embedding <=> %s::vector
        LIMIT %s
        """
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        recommendations = []
        for row in results:
            recommendations.append(
                Recommendation(
                    film=Film(
                        id=row["id"],
                        title=row["title"],
                        year=row["year"],
                        genres=row["genres"],
                        cast=row["cast"],
                        synopsis=row["synopsis"],
                        meta=row["meta"]
                    ),
                    distance=float(row["distance"])
                )
            )
        
        return RecommendationResponse(
            query_text=q,
            recommendations=recommendations,
            count=len(recommendations)
        )
        
    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        error_msg = str(e).replace('\n', ' ')
        raise HTTPException(
            status_code=503,
            detail=f"Erreur de connexion à PostgreSQL: {error_msg}"
        )
    except OSError as e:
        if "1455" in str(e) or "paging file" in str(e).lower() or "fichier de pagination" in str(e).lower():
            error_msg = (
                "Erreur de mémoire insuffisante. "
                "Le système manque de mémoire virtuelle. "
                "Solutions: augmentez le fichier de pagination Windows, "
                "fermez d'autres applications, ou redémarrez votre ordinateur."
            )
            raise HTTPException(status_code=503, detail=error_msg)
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur système: {str(e)}"
            )
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche: {error_msg}"
        )
    finally:
        if conn:
            conn.close()


@app.get("/films/{film_id}", response_model=Film, tags=["Films"])
def get_film(film_id: int):
    """Récupère les détails d'un film par son ID."""
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        cur.execute("""
            SELECT id, title, year, genres, "cast", synopsis, meta
            FROM films
            WHERE id = %s
        """, (film_id,))
        
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Film avec l'id {film_id} non trouvé")
        
        return Film(
            id=row["id"],
            title=row["title"],
            year=row["year"],
            genres=row["genres"],
            cast=row["cast"],
            synopsis=row["synopsis"],
            meta=row["meta"]
        )
        
    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        error_msg = str(e).replace('\n', ' ')
        raise HTTPException(
            status_code=503,
            detail=f"Erreur de connexion à PostgreSQL: {error_msg}"
        )
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur: {error_msg}"
        )
    finally:
        if conn:
            conn.close()


@app.get("/api/poster/{title}", tags=["Images"])
def get_film_poster(title: str, year: Optional[int] = Query(None, description="Année du film")):
    """
    Récupère l'URL de l'affiche d'un film depuis TMDB ou la base de données.
    """
    import urllib.parse
    
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        # Vérifier si on a déjà les métadonnées en base
        cur.execute("""
            SELECT fm.poster_url 
            FROM film_metadata fm
            JOIN films f ON f.id = fm.film_id
            WHERE LOWER(f.title) = LOWER(%s)
        """, (title,))
        
        result = cur.fetchone()
        if result and result.get("poster_url"):
            return {"poster_url": result["poster_url"]}
        
        # Chercher le film pour obtenir l'année
        cur.execute("SELECT year FROM films WHERE LOWER(title) = LOWER(%s) LIMIT 1", (title,))
        film = cur.fetchone()
        film_year = year or (film["year"] if film else None)
        
        # Essayer TMDB
        poster_url = get_movie_poster_url(title, film_year)
        if poster_url:
            return {"poster_url": poster_url}
        
    except Exception as e:
        pass
    finally:
        if conn:
            conn.close()
    
    # Fallback: placeholder
    encoded_title = urllib.parse.quote(title)
    placeholder_url = f"https://via.placeholder.com/300x450/6366f1/ffffff?text={encoded_title}"
    return {"poster_url": placeholder_url}


@app.get("/api/film/{film_id}/metadata", tags=["Films"])
async def get_film_metadata_endpoint(film_id: int):
    """Récupère les métadonnées complètes d'un film (affiche, trailer, streaming)."""
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        # Récupérer le film
        cur.execute("SELECT id, title, year FROM films WHERE id = %s", (film_id,))
        film = cur.fetchone()
        if not film:
            raise HTTPException(status_code=404, detail="Film non trouvé")
        
        # Vérifier si on a déjà les métadonnées en cache
        cur.execute("""
            SELECT poster_url, backdrop_url, trailer_url, trailer_youtube_id, 
                   streaming_platforms, tmdb_id
            FROM film_metadata
            WHERE film_id = %s
        """, (film_id,))
        
        cached = cur.fetchone()
        if cached and cached.get("poster_url"):
            return {
                "poster_url": cached["poster_url"],
                "backdrop_url": cached["backdrop_url"],
                "trailer_url": cached["trailer_url"],
                "trailer_youtube_id": cached["trailer_youtube_id"],
                "streaming_platforms": cached["streaming_platforms"] or []
            }
        
        # Récupérer depuis TMDB
        metadata = get_film_metadata(film["title"], film["year"])
        
        # Sauvegarder en base
        if metadata.get("poster_url"):
            cur.execute("""
                INSERT INTO film_metadata 
                (film_id, poster_url, backdrop_url, trailer_url, trailer_youtube_id, 
                 streaming_platforms, tmdb_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (film_id) DO UPDATE SET
                    poster_url = EXCLUDED.poster_url,
                    backdrop_url = EXCLUDED.backdrop_url,
                    trailer_url = EXCLUDED.trailer_url,
                    trailer_youtube_id = EXCLUDED.trailer_youtube_id,
                    streaming_platforms = EXCLUDED.streaming_platforms,
                    tmdb_id = EXCLUDED.tmdb_id,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                film_id,
                metadata.get("poster_url"),
                metadata.get("backdrop_url"),
                metadata.get("trailer_url"),
                metadata.get("trailer_youtube_id"),
                metadata.get("streaming_platforms", []),
                metadata.get("tmdb_id")
            ))
            conn.commit()
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.get("/stats", tags=["Statistiques"])
def get_stats():
    """Retourne des statistiques sur la base de données."""
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        # Nombre total de films
        cur.execute("SELECT COUNT(*) FROM films")
        total_films = cur.fetchone()["count"]
        
        # Nombre d'embeddings
        cur.execute("SELECT COUNT(*) FROM film_embeddings")
        total_embeddings = cur.fetchone()["count"]
        
        # Année min/max
        cur.execute("SELECT MIN(year) as min_year, MAX(year) as max_year FROM films WHERE year IS NOT NULL")
        year_stats = cur.fetchone()
        
        # Nombre de genres uniques
        cur.execute("SELECT COUNT(DISTINCT unnest(genres)) FROM films WHERE genres IS NOT NULL")
        unique_genres = cur.fetchone()["count"]
        
        # Taille de l'index
        cur.execute("""
            SELECT pg_size_pretty(pg_relation_size('film_embeddings_hnsw_cosine')) as index_size
        """)
        index_size = cur.fetchone()["index_size"] if cur.rowcount > 0 else "N/A"
        
        return {
            "total_films": total_films,
            "total_embeddings": total_embeddings,
            "min_year": year_stats["min_year"],
            "max_year": year_stats["max_year"],
            "unique_genres": unique_genres,
            "index_size": index_size
        }
        
    except psycopg2.OperationalError as e:
        error_msg = str(e).replace('\n', ' ')
        raise HTTPException(
            status_code=503,
            detail=f"Erreur de connexion à PostgreSQL: {error_msg}"
        )
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des statistiques: {error_msg}"
        )
    finally:
        if conn:
            conn.close()


# ==================== ENDPOINTS D'AUTHENTIFICATION ====================

@app.post("/api/auth/register", tags=["Authentification"])
async def register(request: RegisterRequest, http_request: Request):
    """Inscription d'un nouvel utilisateur."""
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        # Vérifier si l'utilisateur existe déjà
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                   (request.username, request.email))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="Username ou email déjà utilisé")
        
        # Créer l'utilisateur
        password_hash = hash_password(request.password)
        avatar_url = get_avatar_url(request.gender)
        
        cur.execute("""
            INSERT INTO users (username, email, password_hash, gender, avatar_url, role)
            VALUES (%s, %s, %s, %s, %s, 'user')
            RETURNING id, username, email, role, gender, avatar_url
        """, (request.username, request.email, password_hash, request.gender, avatar_url))
        
        user = cur.fetchone()
        conn.commit()
        
        # Créer la session
        ip_address = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent")
        session_token = create_session(user["id"], ip_address, user_agent)
        
        response = JSONResponse({
            "user": dict(user),
            "message": "Inscription réussie"
        })
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            max_age=30 * 24 * 60 * 60,  # 30 jours
            samesite="lax"
        )
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'inscription: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.post("/api/auth/login", tags=["Authentification"])
async def login(request: LoginRequest, http_request: Request):
    """Connexion d'un utilisateur."""
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        cur.execute("""
            SELECT id, username, email, password_hash, role, gender, avatar_url, 
                   is_active, is_blocked
            FROM users
            WHERE username = %s OR email = %s
        """, (request.username, request.username))
        
        user = cur.fetchone()
        if not user or not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Identifiants incorrects")
        
        if not user["is_active"] or user["is_blocked"]:
            raise HTTPException(status_code=403, detail="Compte désactivé ou bloqué")
        
        # Mettre à jour last_login
        cur.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s", 
                   (user["id"],))
        conn.commit()
        
        # Créer la session
        ip_address = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent")
        session_token = create_session(user["id"], ip_address, user_agent)
        
        response = JSONResponse({
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "gender": user["gender"],
                "avatar_url": user["avatar_url"]
            },
            "message": "Connexion réussie"
        })
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            max_age=30 * 24 * 60 * 60,
            samesite="lax"
        )
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la connexion: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.post("/api/auth/logout", tags=["Authentification"])
async def logout(request: Request):
    """Déconnexion d'un utilisateur."""
    session_token = request.cookies.get("session_token")
    if session_token:
        delete_session(session_token)
    
    response = JSONResponse({"message": "Déconnexion réussie"})
    response.delete_cookie("session_token")
    return response


@app.get("/api/auth/me", tags=["Authentification"])
async def get_current_user_info(request: Request):
    """Récupère les informations de l'utilisateur connecté."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    return user


# ==================== ENDPOINTS UTILISATEUR ====================

@app.get("/api/search-history", tags=["Utilisateur"])
async def get_search_history(request: Request, limit: int = Query(50, ge=1, le=100)):
    """Récupère l'historique des recherches de l'utilisateur."""
    user = await require_auth(request)
    conn = None
    try:
        conn, cur = get_connection_dict()
        cur.execute("""
            SELECT id, query_text, filters, results_count, created_at
            FROM search_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user["id"], limit))
        
        history = [dict(row) for row in cur.fetchall()]
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.post("/api/films/{film_id}/watch", tags=["Utilisateur"])
async def mark_film_watched(film_id: int, request: Request, 
                           rating: Optional[int] = Query(None, ge=1, le=5)):
    """Marque un film comme visionné."""
    user = await require_auth(request)
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        # Vérifier que le film existe
        cur.execute("SELECT id FROM films WHERE id = %s", (film_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Film non trouvé")
        
        cur.execute("""
            INSERT INTO watched_films (user_id, film_id, rating)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, film_id) DO UPDATE SET
                watched_at = CURRENT_TIMESTAMP,
                rating = EXCLUDED.rating
        """, (user["id"], film_id, rating))
        
        conn.commit()
        return {"message": "Film marqué comme visionné"}
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.get("/api/watched-films", tags=["Utilisateur"])
async def get_watched_films(request: Request, limit: int = Query(50, ge=1, le=100)):
    """Récupère les films visionnés par l'utilisateur."""
    user = await require_auth(request)
    conn = None
    try:
        conn, cur = get_connection_dict()
        cur.execute("""
            SELECT wf.film_id, wf.watched_at, wf.rating,
                   f.title, f.year, f.genres
            FROM watched_films wf
            JOIN films f ON f.id = wf.film_id
            WHERE wf.user_id = %s
            ORDER BY wf.watched_at DESC
            LIMIT %s
        """, (user["id"], limit))
        
        films = [dict(row) for row in cur.fetchall()]
        return {"films": films}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


# ==================== ENDPOINTS ADMIN ====================

@app.get("/api/admin/dashboard", tags=["Admin"])
async def get_admin_dashboard(request: Request):
    """Tableau de bord admin avec KPI et statistiques."""
    admin = await require_admin(request)
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        # KPI
        cur.execute("SELECT COUNT(*) as total FROM users")
        total_users = cur.fetchone()["total"]
        
        cur.execute("SELECT COUNT(*) as total FROM users WHERE role = 'admin'")
        total_admins = cur.fetchone()["total"]
        
        cur.execute("SELECT COUNT(*) as total FROM user_sessions WHERE is_active = TRUE")
        active_sessions = cur.fetchone()["total"]
        
        cur.execute("SELECT COUNT(*) as total FROM search_history")
        total_searches = cur.fetchone()["total"]
        
        cur.execute("SELECT COUNT(*) as total FROM watched_films")
        total_watched = cur.fetchone()["total"]
        
        # Utilisateurs actifs aujourd'hui
        cur.execute("""
            SELECT COUNT(DISTINCT user_id) as total
            FROM user_sessions
            WHERE created_at >= CURRENT_DATE AND is_active = TRUE
        """)
        active_today = cur.fetchone()["total"]
        
        # Recherches aujourd'hui
        cur.execute("""
            SELECT COUNT(*) as total
            FROM search_history
            WHERE created_at >= CURRENT_DATE
        """)
        searches_today = cur.fetchone()["total"]
        
        # Top genres recherchés
        cur.execute("""
            SELECT unnest(filters->'genres') as genre, COUNT(*) as count
            FROM search_history
            WHERE filters->'genres' IS NOT NULL
            GROUP BY genre
            ORDER BY count DESC
            LIMIT 10
        """)
        top_genres = [dict(row) for row in cur.fetchall()]
        
        # Utilisateurs par jour (7 derniers jours)
        cur.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        users_by_day = [dict(row) for row in cur.fetchall()]
        
        # Recherches par jour (7 derniers jours)
        cur.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM search_history
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        searches_by_day = [dict(row) for row in cur.fetchall()]
        
        return {
            "kpi": {
                "total_users": total_users,
                "total_admins": total_admins,
                "active_sessions": active_sessions,
                "total_searches": total_searches,
                "total_watched": total_watched,
                "active_today": active_today,
                "searches_today": searches_today
            },
            "top_genres": top_genres,
            "users_by_day": users_by_day,
            "searches_by_day": searches_by_day
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.get("/api/admin/users", tags=["Admin"])
async def get_all_users(request: Request, limit: int = Query(100, ge=1, le=500)):
    """Récupère tous les utilisateurs (admin seulement)."""
    admin = await require_admin(request)
    conn = None
    try:
        conn, cur = get_connection_dict()
        cur.execute("""
            SELECT id, username, email, role, gender, avatar_url, 
                   is_active, is_blocked, created_at, last_login
            FROM users
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
        
        users = [dict(row) for row in cur.fetchall()]
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.get("/api/admin/sessions", tags=["Admin"])
async def get_all_sessions(request: Request, limit: int = Query(100, ge=1, le=500)):
    """Récupère toutes les sessions actives (admin seulement)."""
    admin = await require_admin(request)
    conn = None
    try:
        conn, cur = get_connection_dict()
        cur.execute("""
            SELECT s.id, s.user_id, u.username, s.ip_address, s.user_agent,
                   s.created_at, s.expires_at, s.is_active
            FROM user_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.is_active = TRUE
            ORDER BY s.created_at DESC
            LIMIT %s
        """, (limit,))
        
        sessions = [dict(row) for row in cur.fetchall()]
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.get("/api/admin/search-history", tags=["Admin"])
async def get_all_search_history(request: Request, limit: int = Query(100, ge=1, le=500)):
    """Récupère tout l'historique de recherche (admin seulement)."""
    admin = await require_admin(request)
    conn = None
    try:
        conn, cur = get_connection_dict()
        cur.execute("""
            SELECT sh.id, sh.user_id, u.username, sh.query_text, 
                   sh.filters, sh.results_count, sh.created_at
            FROM search_history sh
            JOIN users u ON u.id = sh.user_id
            ORDER BY sh.created_at DESC
            LIMIT %s
        """, (limit,))
        
        history = [dict(row) for row in cur.fetchall()]
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.post("/api/admin/users/{user_id}/block", tags=["Admin"])
async def block_user(user_id: int, request: Request):
    """Bloque un utilisateur (admin seulement)."""
    admin = await require_admin(request)
    conn = None
    try:
        conn, cur = get_connection_dict()
        cur.execute("UPDATE users SET is_blocked = TRUE WHERE id = %s", (user_id,))
        conn.commit()
        return {"message": "Utilisateur bloqué"}
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.post("/api/admin/users/{user_id}/unblock", tags=["Admin"])
async def unblock_user(user_id: int, request: Request):
    """Débloque un utilisateur (admin seulement)."""
    admin = await require_admin(request)
    conn = None
    try:
        conn, cur = get_connection_dict()
        cur.execute("UPDATE users SET is_blocked = FALSE WHERE id = %s", (user_id,))
        conn.commit()
        return {"message": "Utilisateur débloqué"}
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.delete("/api/admin/users/{user_id}", tags=["Admin"])
async def delete_user(user_id: int, request: Request):
    """Supprime un utilisateur (admin seulement)."""
    admin = await require_admin(request)
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")
    
    conn = None
    try:
        conn, cur = get_connection_dict()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return {"message": "Utilisateur supprimé"}
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


# Mise à jour de l'endpoint de recherche pour enregistrer l'historique
@app.get("/search", response_model=RecommendationResponse, tags=["Recherche"])
async def search(
    q: str = Query(..., description="Requête textuelle de recherche"),
    k: int = Query(10, ge=1, le=100, description="Nombre de résultats"),
    genres: Optional[str] = Query(None, description="Genres requis, séparés par des virgules"),
    min_year: Optional[int] = Query(None, description="Année minimum"),
    max_year: Optional[int] = Query(None, description="Année maximum"),
    request: Request = None
):
    """
    Recherche sémantique de films à partir d'une requête textuelle.
    
    La requête est convertie en embedding et comparée avec les embeddings des films.
    """
    conn = None
    try:
        # Générer l'embedding de la requête
        model = get_model()
        query_embedding = model.encode([q], normalize_embeddings=True)[0]
        vec_str = "[" + ",".join(f"{x:.8f}" for x in query_embedding.tolist()) + "]"
        
        conn, cur = get_connection_dict()
        
        # Construire la requête avec filtres
        filters = []
        filter_params = []
        
        if genres:
            genres_list = [g.strip() for g in genres.split(",")]
            for genre in genres_list:
                filters.append("%s = ANY(f.genres)")
                filter_params.append(genre)
        
        if min_year:
            filters.append("f.year >= %s")
            filter_params.append(min_year)
        
        if max_year:
            filters.append("f.year <= %s")
            filter_params.append(max_year)
        
        filter_clause = " AND " + " AND ".join(filters) if filters else ""
        
        # Ordre des paramètres : vec_str (SELECT), filtres, vec_str (ORDER BY), k (LIMIT)
        params = [vec_str] + filter_params + [vec_str, k]
        
        query = f"""
        SELECT 
            f.id, f.title, f.year, f.genres, f."cast", f.synopsis, f.meta,
            (fe.embedding <=> %s::vector) AS distance
        FROM film_embeddings fe
        JOIN films f ON f.id = fe.film_id
        WHERE 1=1
        {filter_clause}
        ORDER BY fe.embedding <=> %s::vector
        LIMIT %s
        """
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        recommendations = []
        for row in results:
            recommendations.append(
                Recommendation(
                    film=Film(
                        id=row["id"],
                        title=row["title"],
                        year=row["year"],
                        genres=row["genres"],
                        cast=row["cast"],
                        synopsis=row["synopsis"],
                        meta=row["meta"]
                    ),
                    distance=float(row["distance"])
                )
            )
        
        # Enregistrer dans l'historique si l'utilisateur est connecté
        try:
            user = await get_current_user(request)
            if user:
                import json
                filters_dict = {}
                if genres:
                    filters_dict["genres"] = genres.split(",")
                if min_year:
                    filters_dict["min_year"] = min_year
                if max_year:
                    filters_dict["max_year"] = max_year
                
                cur.execute("""
                    INSERT INTO search_history (user_id, query_text, filters, results_count)
                    VALUES (%s, %s, %s, %s)
                """, (user["id"], q, json.dumps(filters_dict), len(recommendations)))
                conn.commit()
        except:
            pass  # Ignorer les erreurs d'historique
        
        return RecommendationResponse(
            query_text=q,
            recommendations=recommendations,
            count=len(recommendations)
        )
        
    except HTTPException:
        raise
    except psycopg2.OperationalError as e:
        error_msg = str(e).replace('\n', ' ')
        raise HTTPException(
            status_code=503,
            detail=f"Erreur de connexion à PostgreSQL: {error_msg}"
        )
    except OSError as e:
        if "1455" in str(e) or "paging file" in str(e).lower() or "fichier de pagination" in str(e).lower():
            error_msg = (
                "Erreur de mémoire insuffisante. "
                "Le système manque de mémoire virtuelle. "
                "Solutions: augmentez le fichier de pagination Windows, "
                "fermez d'autres applications, ou redémarrez votre ordinateur."
            )
            raise HTTPException(status_code=503, detail=error_msg)
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur système: {str(e)}"
            )
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche: {error_msg}"
        )
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)

