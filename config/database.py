"""
Configuration et utilitaires pour la connexion à la base de données PostgreSQL.
"""
import os
import sys
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Configurer l'environnement pour gérer les erreurs d'encodage
# Certaines versions de PostgreSQL retournent des messages en latin-1
if sys.platform == 'win32':
    # Sur Windows, utiliser latin-1 pour les erreurs
    import locale
    try:
        # Essayer de définir l'encodage par défaut pour les erreurs
        if hasattr(sys, 'setdefaultencoding'):
            sys.setdefaultencoding('latin-1')
    except:
        pass

# Charger le .env avec gestion d'encodage
try:
    load_dotenv(encoding='utf-8')
except:
    # Fallback si l'encodage UTF-8 échoue
    load_dotenv(encoding='latin-1')

# Configuration de la base de données
# Encoder les valeurs en UTF-8 de manière sûre
def safe_encode(value):
    """Encode une valeur en UTF-8 de manière sûre"""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return str(value).encode('utf-8', errors='replace').decode('utf-8')

DB_CONFIG = {
    "dbname": safe_encode(os.getenv("DB_NAME", "filmsrec")),
    "user": safe_encode(os.getenv("DB_USER", "postgres")),
    "password": safe_encode(os.getenv("DB_PASSWORD", "")),
    "host": safe_encode(os.getenv("DB_HOST", "localhost")),
    "port": safe_encode(os.getenv("DB_PORT", "5432")),
}

# Pool de connexions (optionnel, pour améliorer les performances)
connection_pool = None


def get_connection_pool():
    """Crée un pool de connexions pour l'API."""
    global connection_pool
    if connection_pool is None:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            **DB_CONFIG
        )
    return connection_pool


def get_connection():
    """Retourne une nouvelle connexion à la base de données."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        # Définir l'encodage de la connexion
        conn.set_client_encoding('UTF8')
        return conn
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        # Le message d'erreur de PostgreSQL contient des caractères non-UTF-8
        # Cela indique généralement un problème de mot de passe ou de configuration
        error_msg = (
            "Erreur de connexion à PostgreSQL. "
            "Vérifiez que:\n"
            "1. PostgreSQL est démarré\n"
            "2. Le mot de passe dans .env est correct\n"
            "3. La base de données '{}' existe\n"
            "4. L'utilisateur '{}' a les permissions nécessaires"
        ).format(DB_CONFIG.get('dbname', 'filmsrec'), DB_CONFIG.get('user', 'postgres'))
        raise psycopg2.OperationalError(error_msg) from None
    except psycopg2.OperationalError as e:
        # Capturer l'erreur et la reformater de manière sûre
        try:
            error_str = str(e)
        except (UnicodeDecodeError, UnicodeEncodeError):
            error_str = "Erreur de connexion (détails non disponibles - problème d'encodage)"
        
        # Vérifier le type d'erreur
        if "password" in error_str.lower() or "mot de passe" in error_str.lower():
            error_msg = (
                "Erreur d'authentification PostgreSQL. "
                "Le mot de passe dans .env est probablement incorrect."
            )
        elif "does not exist" in error_str.lower() or "n'existe pas" in error_str.lower():
            error_msg = (
                "La base de données '{}' n'existe pas. "
                "Créez-la avec: CREATE DATABASE {};"
            ).format(DB_CONFIG.get('dbname', 'filmsrec'), DB_CONFIG.get('dbname', 'filmsrec'))
        elif "could not connect" in error_str.lower() or "ne peut pas se connecter" in error_str.lower():
            error_msg = (
                "Impossible de se connecter à PostgreSQL sur {}:{}. "
                "Vérifiez que PostgreSQL est démarré."
            ).format(DB_CONFIG.get('host', 'localhost'), DB_CONFIG.get('port', '5432'))
        else:
            error_msg = f"Erreur de connexion à PostgreSQL: {error_str}"
        
        raise psycopg2.OperationalError(error_msg) from None
    except Exception as e:
        # Autres erreurs
        error_msg = (
            "Erreur inattendue lors de la connexion à PostgreSQL: {}. "
            "Vérifiez votre configuration dans .env"
        ).format(str(e))
        raise psycopg2.OperationalError(error_msg) from None


def get_connection_dict():
    """Retourne une connexion avec RealDictCursor pour obtenir des dictionnaires."""
    conn = get_connection()
    return conn, conn.cursor(cursor_factory=RealDictCursor)


def close_connection_pool():
    """Ferme le pool de connexions."""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        connection_pool = None

