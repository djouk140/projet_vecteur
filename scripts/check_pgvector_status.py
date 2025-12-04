"""
Script pour vérifier le statut de pgvector
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import psycopg2

dbname = os.getenv("DB_NAME", "filmsrec")
user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD", "root")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")

print("Vérification du statut de pgvector...")
print("="*60)

try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()
    
    # Vérifier si pgvector est disponible
    cur.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
    available = cur.fetchone()
    
    if available:
        print("✓ Extension pgvector disponible dans PostgreSQL")
        
        # Vérifier si elle est activée
        cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
        enabled = cur.fetchone()
        
        if enabled:
            print("✓ Extension pgvector activée dans la base de données")
            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            version = cur.fetchone()[0]
            print(f"  Version: {version}")
        else:
            print("⚠ Extension pgvector disponible mais non activée")
            print("  Pour l'activer, exécutez:")
            print(f"  CREATE EXTENSION IF NOT EXISTS vector;")
    else:
        print("✗ Extension pgvector NON disponible")
        print("  Vous devez installer pgvector sur votre système PostgreSQL")
        print("  Voir: docs/INSTALL_PGVECTOR_WINDOWS.md")
        
        # Vérifier les fichiers sur le disque
        print("\nVérification des fichiers sur le disque...")
        pg_paths = [
            "C:\\Program Files\\PostgreSQL\\18\\lib\\vector.dll",
            "C:\\Program Files\\PostgreSQL\\17\\lib\\vector.dll"
        ]
        
        for path in pg_paths:
            if Path(path).exists():
                print(f"✓ Fichier trouvé: {path}")
            else:
                print(f"✗ Fichier manquant: {path}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Erreur: {e}")

