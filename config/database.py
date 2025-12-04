"""
Configuration et utilitaires pour la connexion à la base de données PostgreSQL.
"""
import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "filmsrec"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
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
    return psycopg2.connect(**DB_CONFIG)


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

