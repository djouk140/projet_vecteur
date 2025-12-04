"""
Script pour créer la base de données si elle n'existe pas
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

print(f"Création de la base de données '{dbname}' si elle n'existe pas...")

# Se connecter à la base de données 'postgres' par défaut
try:
    # Essayer d'abord de se connecter à la base cible
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    print(f"✓ La base de données '{dbname}' existe déjà")
    conn.close()
except psycopg2.OperationalError as e:
    error_str = str(e)
    if "does not exist" in error_str or "n'existe pas" in error_str:
        print(f"⚠ La base de données '{dbname}' n'existe pas")
        print("  Tentative de création...")
        
        # Se connecter à la base 'postgres' pour créer la nouvelle base
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
            cur.execute(f"CREATE DATABASE {dbname};")
            cur.close()
            conn.close()
            print(f"✓ Base de données '{dbname}' créée avec succès")
        except Exception as create_error:
            print(f"✗ Erreur lors de la création: {create_error}")
            print("\nVous pouvez créer la base manuellement avec:")
            print(f"  psql -U {user} -c \"CREATE DATABASE {dbname};\"")
    else:
        print(f"✗ Erreur de connexion: {error_str}")
        print("  Vérifiez votre mot de passe dans le fichier .env")
except UnicodeDecodeError:
    print("✗ Erreur d'encodage lors de la connexion")
    print("  Le message d'erreur de PostgreSQL contient des caractères non-UTF-8")
    print("  Cela indique probablement que:")
    print("    1. Le mot de passe est incorrect")
    print("    2. L'utilisateur n'existe pas")
    print("    3. Les permissions sont incorrectes")
except Exception as e:
    print(f"✗ Erreur inattendue: {type(e).__name__}: {e}")

