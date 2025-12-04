"""
Script de vérification de l'installation et de la configuration.
Vérifie que tous les composants sont correctement installés et configurés.
"""
import sys
import os
from pathlib import Path

def check_file(filepath, description):
    """Vérifie qu'un fichier existe."""
    if Path(filepath).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - FICHIER MANQUANT")
        return False

def check_python_packages():
    """Vérifie que les packages Python sont installés."""
    required_packages = [
        "psycopg2",
        "numpy",
        "pandas",
        "sklearn",
        "sentence_transformers",
        "fastapi",
        "uvicorn",
        "dotenv"
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == "dotenv":
                __import__("dotenv")
            elif package == "sklearn":
                __import__("sklearn")
            else:
                __import__(package)
            print(f"✓ Package Python: {package}")
        except ImportError:
            print(f"✗ Package Python manquant: {package}")
            missing.append(package)
    
    return len(missing) == 0

def check_env_file():
    """Vérifie la présence du fichier .env."""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if env_file.exists():
        print("✓ Fichier .env présent")
        return True
    elif env_example.exists():
        print("⚠ Fichier .env manquant, mais env_example.txt présent")
        print("  Créez .env en copiant env_example.txt")
        return False
    else:
        print("✗ Fichier .env manquant et pas d'exemple trouvé")
        return False

def check_database_connection():
    """Vérifie la connexion à la base de données."""
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from config.database import get_connection
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✓ Connexion à PostgreSQL réussie")
        print(f"  Version: {version.split(',')[0]}")
        
        # Vérifier l'extension pgvector
        cur.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
        if cur.fetchone():
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
            if cur.fetchone():
                print("✓ Extension pgvector installée et activée")
            else:
                print("⚠ Extension pgvector disponible mais non activée")
        else:
            print("✗ Extension pgvector non disponible")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Erreur de connexion à la base de données: {e}")
        return False

def check_database_schema():
    """Vérifie que les tables existent."""
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from config.database import get_connection
        
        conn = get_connection()
        cur = conn.cursor()
        
        # Vérifier les tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name IN ('films', 'film_embeddings')
        """)
        tables = {row[0] for row in cur.fetchall()}
        
        expected_tables = {"films", "film_embeddings"}
        missing_tables = expected_tables - tables
        
        if not missing_tables:
            print("✓ Tables de la base de données présentes")
            
            # Vérifier les données
            cur.execute("SELECT COUNT(*) FROM films")
            film_count = cur.fetchone()[0]
            print(f"  Films dans la base: {film_count}")
            
            cur.execute("SELECT COUNT(*) FROM film_embeddings")
            embedding_count = cur.fetchone()[0]
            print(f"  Embeddings dans la base: {embedding_count}")
            
            # Vérifier l'index
            cur.execute("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'film_embeddings'
                AND indexname LIKE '%hnsw%'
            """)
            if cur.fetchone():
                print("✓ Index HNSW créé")
            else:
                print("⚠ Index HNSW non créé (à faire après génération des embeddings)")
            
            cur.close()
            conn.close()
            return True
        else:
            print(f"✗ Tables manquantes: {', '.join(missing_tables)}")
            print("  Exécutez: python scripts/setup_database.py")
            cur.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ Erreur lors de la vérification du schéma: {e}")
        return False

def main():
    """Fonction principale de vérification."""
    print("="*60)
    print("VÉRIFICATION DE L'INSTALLATION")
    print("="*60)
    print()
    
    results = []
    
    # 1. Vérifier les fichiers essentiels
    print("1. Vérification des fichiers...")
    print("-" * 40)
    results.append(check_file("requirements.txt", "requirements.txt"))
    results.append(check_file("README.md", "README.md"))
    results.append(check_file("sql/schema.sql", "Schéma SQL"))
    results.append(check_file("scripts/ingest_films.py", "Script d'ingestion"))
    results.append(check_file("scripts/generate_embeddings.py", "Script d'embeddings"))
    results.append(check_file("api/main.py", "API FastAPI"))
    print()
    
    # 2. Vérifier les packages Python
    print("2. Vérification des packages Python...")
    print("-" * 40)
    results.append(check_python_packages())
    print()
    
    # 3. Vérifier le fichier .env
    print("3. Vérification de la configuration...")
    print("-" * 40)
    results.append(check_env_file())
    print()
    
    # 4. Vérifier la base de données (si .env existe)
    if Path(".env").exists():
        print("4. Vérification de la base de données...")
        print("-" * 40)
        db_conn = check_database_connection()
        print()
        
        if db_conn:
            print("5. Vérification du schéma de base de données...")
            print("-" * 40)
            results.append(check_database_schema())
            print()
    
    # Résumé
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"RÉSUMÉ: {passed}/{total} vérifications réussies")
    print("="*60)
    
    if passed == total:
        print("✓ Installation complète et correcte!")
        return True
    else:
        print("⚠ Certaines vérifications ont échoué. Consultez le README.md pour plus d'informations.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

