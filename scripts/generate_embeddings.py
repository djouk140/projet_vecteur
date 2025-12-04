"""
Script de génération des embeddings pour les films.
Rôle 2: Embeddings et indexation
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

import numpy as np
from sentence_transformers import SentenceTransformer
from config.database import get_connection
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

def build_film_text(film_data, include_title=True, include_synopsis=True, 
                    include_genres=True, include_cast=True):
    """
    Construit le texte pour générer l'embedding d'un film.
    
    Args:
        film_data: tuple (id, title, synopsis, genres, cast)
        include_title: inclure le titre
        include_synopsis: inclure le synopsis
        include_genres: inclure les genres
        include_cast: inclure le cast
    
    Returns:
        Texte formaté pour l'embedding
    """
    film_id, title, synopsis, genres, cast = film_data
    
    parts = []
    
    if include_title and title:
        parts.append(str(title))
    
    if include_synopsis and synopsis:
        parts.append(str(synopsis))
    
    if include_genres and genres:
        genres_str = ", ".join(genres) if isinstance(genres, list) else str(genres)
        parts.append(f"Genres: {genres_str}")
    
    if include_cast and cast:
        cast_str = ", ".join(cast) if isinstance(cast, list) else str(cast)
        parts.append(f"Cast: {cast_str}")
    
    return " ; ".join(parts)


def generate_embeddings(model_name=None, batch_size=32, normalize=True):
    """
    Génère les embeddings pour tous les films.
    
    Args:
        model_name: nom du modèle SentenceTransformer (par défaut depuis .env)
        batch_size: taille des lots pour la génération
        normalize: normaliser les embeddings (recommandé pour distance cosinus)
    """
    if model_name is None:
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
    
    print(f"Chargement du modèle: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Vérifier la dimension
    sample_embedding = model.encode(["test"], normalize_embeddings=normalize)[0]
    embedding_dim = len(sample_embedding)
    print(f"Dimension des embeddings: {embedding_dim}")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Récupérer tous les films
    cur.execute('SELECT id, title, synopsis, genres, "cast" FROM films ORDER BY id')
    films = cur.fetchall()
    
    print(f"Nombre de films à traiter: {len(films)}")
    
    # Génération par lots
    total_generated = 0
    
    for i in range(0, len(films), batch_size):
        batch = films[i:i + batch_size]
        
        # Construire les textes
        texts = [build_film_text(film) for film in batch]
        
        # Générer les embeddings
        print(f"Génération des embeddings pour le lot {i//batch_size + 1}...")
        embeddings = model.encode(texts, normalize_embeddings=normalize, show_progress_bar=False)
        
        # Préparer les données pour insertion par lots
        insert_data = []
        for film_data, embedding in zip(batch, embeddings):
            film_id = film_data[0]
            vec_str = "[" + ",".join(f"{x:.8f}" for x in embedding.tolist()) + "]"
            insert_data.append((film_id, vec_str))
        
        # Insérer par lots (plus rapide)
        execute_values(
            cur,
            """
            INSERT INTO film_embeddings (film_id, embedding)
            VALUES %s
            ON CONFLICT (film_id) DO UPDATE SET embedding = EXCLUDED.embedding
            """,
            insert_data,
            template=None,
            page_size=batch_size
        )
        
        total_generated += len(insert_data)
        conn.commit()
        print(f"Lot {i//batch_size + 1} terminé: {total_generated}/{len(films)} embeddings générés")
    
    # Statistiques finales
    cur.execute("SELECT COUNT(*) FROM film_embeddings")
    total_in_db = cur.fetchone()[0]
    print(f"\nTotal d'embeddings dans la base: {total_in_db}")
    
    cur.close()
    conn.close()
    print("Génération des embeddings terminée avec succès!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Générer les embeddings pour les films")
    parser.add_argument("--model", type=str, default=None, help="Nom du modèle SentenceTransformer")
    parser.add_argument("--batch-size", type=int, default=32, help="Taille des lots")
    parser.add_argument("--no-normalize", action="store_true", help="Ne pas normaliser les embeddings")
    
    args = parser.parse_args()
    
    generate_embeddings(
        model_name=args.model,
        batch_size=args.batch_size,
        normalize=not args.no_normalize
    )

