"""
Script principal pour exécuter toute la chaîne : ingestion -> embeddings -> index.
Utile pour un setup complet en une seule commande.
"""
import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from scripts.setup_database import main as setup_db
from scripts.ingest_films import ingest_from_csv
from scripts.generate_embeddings import generate_embeddings
from config.database import get_connection


def create_index():
    """Crée l'index HNSW."""
    print("\n" + "="*60)
    print("Création de l'index HNSW")
    print("="*60)
    
    index_path = Path(__file__).parent.parent / "sql" / "index_hnsw.sql"
    
    if not index_path.exists():
        print(f"✗ Fichier index_hnsw.sql non trouvé: {index_path}")
        return False
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Lire le fichier SQL (gestion de l'encodage)
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_sql = f.read()
        except UnicodeDecodeError:
            # Fallback si UTF-8 échoue
            with open(index_path, 'r', encoding='latin-1') as f:
                index_sql = f.read()
        
        print("Création de l'index (cela peut prendre du temps)...")
        cur.execute(index_sql)
        conn.commit()
        
        print("✓ Index HNSW créé avec succès")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors de la création de l'index: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Exécute toute la chaîne : setup DB -> ingestion -> embeddings -> index"
    )
    parser.add_argument(
        "--csv",
        help="Chemin vers le fichier CSV à ingérer (optionnel si déjà ingéré)"
    )
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Ignorer la configuration de la base de données"
    )
    parser.add_argument(
        "--skip-ingestion",
        action="store_true",
        help="Ignorer l'ingestion (si les données sont déjà présentes)"
    )
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Ignorer la génération d'embeddings"
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="Ignorer la création de l'index"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("CHAÎNE COMPLÈTE DE TRAITEMENT")
    print("="*60)
    
    # 1. Setup database
    if not args.skip_setup:
        print("\n[1/4] Configuration de la base de données...")
        if not setup_db():
            print("✗ Échec de la configuration. Arrêt.")
            return False
    else:
        print("\n[1/4] Configuration de la base de données... (ignoré)")
    
    # 2. Ingestion
    if not args.skip_ingestion:
        if args.csv:
            print(f"\n[2/4] Ingestion depuis {args.csv}...")
            try:
                ingest_from_csv(args.csv)
            except Exception as e:
                print(f"✗ Erreur lors de l'ingestion: {e}")
                return False
        else:
            print("\n[2/4] Ingestion... (ignoré, pas de fichier CSV fourni)")
    else:
        print("\n[2/4] Ingestion... (ignoré)")
    
    # 3. Embeddings
    if not args.skip_embeddings:
        print("\n[3/4] Génération des embeddings...")
        try:
            generate_embeddings()
        except Exception as e:
            print(f"✗ Erreur lors de la génération des embeddings: {e}")
            return False
    else:
        print("\n[3/4] Génération des embeddings... (ignoré)")
    
    # 4. Index
    if not args.skip_index:
        print("\n[4/4] Création de l'index HNSW...")
        if not create_index():
            print("✗ Échec de la création de l'index.")
            return False
    else:
        print("\n[4/4] Création de l'index HNSW... (ignoré)")
    
    print("\n" + "="*60)
    print("✓ CHAÎNE COMPLÈTE TERMINÉE AVEC SUCCÈS!")
    print("="*60)
    print("\nVous pouvez maintenant lancer l'API avec:")
    print("  uvicorn api.main:app --reload")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

