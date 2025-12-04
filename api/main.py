"""
API FastAPI pour les recommandations de films avec pgvector.
Rôle 3: API et intégration
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_connection, get_connection_dict, close_connection_pool
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

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

def get_model():
    """Retourne le modèle d'embeddings (chargé en lazy loading)."""
    global _model
    if _model is None:
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
        print(f"Chargement du modèle: {model_name}")
        _model = SentenceTransformer(model_name)
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
            f.id, f.title, f.year, f.genres, f.cast, f.synopsis, f.meta,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recommandation: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.get("/search", response_model=RecommendationResponse, tags=["Recherche"])
def search(
    q: str = Query(..., description="Requête textuelle de recherche"),
    k: int = Query(10, ge=1, le=100, description="Nombre de résultats"),
    genres: Optional[str] = Query(None, description="Genres requis, séparés par des virgules"),
    min_year: Optional[int] = Query(None, description="Année minimum"),
    max_year: Optional[int] = Query(None, description="Année maximum")
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
            f.id, f.title, f.year, f.genres, f.cast, f.synopsis, f.meta,
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")
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
            SELECT id, title, year, genres, cast, synopsis, meta
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


@app.get("/api/poster/{title}", tags=["Images"])
def get_film_poster(title: str, year: Optional[int] = Query(None, description="Année du film")):
    """
    Récupère l'URL de l'affiche d'un film.
    Pour l'instant, retourne une image placeholder. 
    Peut être étendu pour utiliser TMDB ou d'autres APIs.
    """
    import urllib.parse
    
    # Vérifier si le film existe dans notre base et a une URL d'affiche
    conn = None
    try:
        conn, cur = get_connection_dict()
        
        # Chercher le film par titre
        query = "SELECT meta FROM films WHERE LOWER(title) = LOWER(%s)"
        params = [title]
        
        if year:
            query += " AND year = %s"
            params.append(year)
        
        query += " LIMIT 1"
        cur.execute(query, params)
        result = cur.fetchone()
        
        if result and result.get("meta") and result["meta"].get("poster_url"):
            return {"poster_url": result["meta"]["poster_url"]}
    except Exception as e:
        # Continue vers placeholder si erreur
        pass
    finally:
        if conn:
            conn.close()
    
    # Fallback: générer une image placeholder avec le titre
    encoded_title = urllib.parse.quote(title)
    placeholder_url = f"https://via.placeholder.com/300x450/6366f1/ffffff?text={encoded_title}"
    
    return {"poster_url": placeholder_url}


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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)

