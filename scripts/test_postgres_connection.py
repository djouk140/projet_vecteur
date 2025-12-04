"""
Script pour tester la connexion PostgreSQL et configurer pgvector
"""
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import psycopg2

# Récupérer les paramètres
dbname = os.getenv("DB_NAME", "filmsrec")
user = os.getenv("DB_USER", "postgres")
password = os.getenv("DB_PASSWORD", "root")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")

print("="*60)
print("TEST DE CONNEXION POSTGRESQL")
print("="*60)
print(f"Utilisateur: {user}")
print(f"Host: {host}")
print(f"Port: {port}")
print(f"Base de données: {dbname}")
print()

# Test 1: Connexion à la base 'postgres'
print("1. Test de connexion à la base 'postgres'...")
try:
    conn = psycopg2.connect(
        dbname='postgres',
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"✓ Connexion réussie!")
    print(f"  Version: {version.split(',')[0]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"✗ Erreur de connexion: {e}")
    sys.exit(1)

# Test 2: Vérifier si la base filmsrec existe
print(f"\n2. Vérification de la base '{dbname}'...")
try:
    conn = psycopg2.connect(
        dbname='postgres',
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()
    
    if exists:
        print(f"✓ La base '{dbname}' existe déjà")
    else:
        print(f"⚠ La base '{dbname}' n'existe pas")
        print(f"  Création de la base...")
        cur.execute(f'CREATE DATABASE "{dbname}";')
        print(f"✓ Base '{dbname}' créée avec succès")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

# Test 3: Connexion à la base filmsrec et vérification pgvector
print(f"\n3. Test de connexion à la base '{dbname}'...")
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()
    print(f"✓ Connexion à '{dbname}' réussie")
    
    # Vérifier pgvector
    print(f"\n4. Vérification de l'extension pgvector...")
    cur.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
    if cur.fetchone():
        cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector'")
        if cur.fetchone():
            print("✓ Extension pgvector déjà activée")
        else:
            print("⚠ Extension pgvector disponible mais non activée")
            print("  Activation de l'extension...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            print("✓ Extension pgvector activée")
    else:
        print("✗ Extension pgvector non disponible")
        print("  Installez pgvector sur votre système PostgreSQL")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✓ TOUS LES TESTS RÉUSSIS!")
print("="*60)
print("\nVous pouvez maintenant:")
print("1. Exécuter: python scripts/setup_database.py")
print("2. Ingérer les données: python scripts/ingest_films.py data/films.csv")
print("3. Générer les embeddings: python scripts/generate_embeddings.py")

