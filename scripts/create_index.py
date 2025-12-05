#!/usr/bin/env python3
"""
Script pour créer l'index HNSW sur les embeddings
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_connection

def create_hnsw_index():
    """Crée l'index HNSW pour la recherche vectorielle."""
    print("=" * 60)
    print("Création de l'index HNSW")
    print("=" * 60)
    print()
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Vérifier le nombre d'embeddings
        cur.execute("SELECT COUNT(*) FROM film_embeddings")
        count = cur.fetchone()[0]
        print(f"Nombre d'embeddings dans la base: {count}")
        
        if count == 0:
            print("⚠ Aucun embedding trouvé. Générez d'abord les embeddings.")
            return
        
        # Créer l'index HNSW
        print("Création de l'index HNSW (cela peut prendre quelques minutes)...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS film_embeddings_hnsw_cosine
            ON film_embeddings USING hnsw (embedding vector_cosine_ops)
        """)
        conn.commit()
        
        # VACUUM doit être exécuté en dehors d'une transaction
        print("Optimisation de la base de données...")
        conn.commit()  # Finaliser la transaction en cours
        conn.autocommit = True  # Activer autocommit pour VACUUM
        cur.execute("VACUUM ANALYZE film_embeddings")
        conn.autocommit = False  # Désactiver autocommit
        
        print("✓ Index HNSW créé avec succès")
        
        # Vérifier l'index
        cur.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'film_embeddings' 
            AND indexname LIKE '%hnsw%'
        """)
        indexes = cur.fetchall()
        if indexes:
            print("\nIndex créé:")
            for idx_name, idx_def in indexes:
                print(f"  - {idx_name}")
        
    except Exception as e:
        print(f"✗ Erreur lors de la création de l'index: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_hnsw_index()

