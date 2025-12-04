"""
Script de test de connexion directe à PostgreSQL
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
password = os.getenv("DB_PASSWORD", "")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")

print("Test de connexion à PostgreSQL...")
print(f"DB_NAME: {dbname}")
print(f"DB_USER: {user}")
print(f"DB_HOST: {host}")
print(f"DB_PORT: {port}")
print(f"DB_PASSWORD: {'*' * len(password) if password else '(vide)'}")

# Essayer différentes méthodes de connexion
print("\n1. Connexion avec paramètres séparés...")
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    print("✓ Connexion réussie!")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"  Version: {version[:50]}...")
    cur.close()
    conn.close()
except UnicodeDecodeError as e:
    print(f"✗ Erreur UnicodeDecodeError: {e}")
    print("  Le problème vient probablement du message d'erreur de PostgreSQL")
except psycopg2.OperationalError as e:
    print(f"✗ Erreur de connexion: {e}")
except Exception as e:
    print(f"✗ Erreur inattendue: {type(e).__name__}: {e}")

print("\n2. Connexion avec DSN string...")
try:
    dsn = f"dbname={dbname} user={user} password={password} host={host} port={port}"
    conn = psycopg2.connect(dsn)
    print("✓ Connexion réussie avec DSN!")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    print(f"  Version: {version[:50]}...")
    cur.close()
    conn.close()
except UnicodeDecodeError as e:
    print(f"✗ Erreur UnicodeDecodeError: {e}")
except psycopg2.OperationalError as e:
    print(f"✗ Erreur de connexion: {e}")
except Exception as e:
    print(f"✗ Erreur inattendue: {type(e).__name__}: {e}")

