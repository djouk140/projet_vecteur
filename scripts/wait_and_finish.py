#!/usr/bin/env python3
"""
Script qui attend la fin de la génération des embeddings et crée l'index.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_connection
from scripts.create_index import create_hnsw_index

def check_progress():
    """Vérifie la progression de la génération des embeddings."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT COUNT(*) FROM film_embeddings')
    embeddings_count = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM films')
    films_count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return embeddings_count, films_count

def main():
    """Attend la fin de la génération et crée l'index."""
    print("=" * 60)
    print("SURVEILLANCE DE LA GÉNÉRATION DES EMBEDDINGS")
    print("=" * 60)
    print()
    
    target_count = None
    
    while True:
        embeddings_count, films_count = check_progress()
        
        if target_count is None:
            target_count = films_count
            print(f"Objectif: {target_count} embeddings à générer")
            print()
        
        percentage = (embeddings_count * 100) // target_count if target_count > 0 else 0
        
        print(f"\rProgression: {embeddings_count}/{target_count} ({percentage}%)", end="", flush=True)
        
        if embeddings_count >= target_count:
            print("\n\n✓ Tous les embeddings ont été générés!")
            break
        
        time.sleep(10)  # Attendre 10 secondes avant de revérifier
    
    print()
    print("=" * 60)
    print("CRÉATION DE L'INDEX HNSW")
    print("=" * 60)
    print()
    
    try:
        create_hnsw_index()
        print()
        print("=" * 60)
        print("✓ CONFIGURATION COMPLÈTE TERMINÉE!")
        print("=" * 60)
        print()
        print("Vous pouvez maintenant lancer l'API avec:")
        print("  uvicorn api.main:app --reload")
        print()
        return True
    except Exception as e:
        print(f"\n✗ Erreur lors de la création de l'index: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

