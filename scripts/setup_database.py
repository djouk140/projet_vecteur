"""
Script utilitaire pour initialiser la base de données.
Exécute le schéma SQL et vérifie la configuration.
"""
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import psycopg2
from config.database import get_connection, DB_CONFIG
from dotenv import load_dotenv

load_dotenv()


def check_pgvector():
    """Vérifie si l'extension pgvector est disponible."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
        result = cur.fetchone()
        
        if result:
            print("✓ Extension pgvector disponible")
            cur.close()
            conn.close()
            return True
        else:
            print("✗ Extension pgvector non disponible")
            cur.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ Erreur lors de la vérification: {e}")
        return False


def setup_schema():
    """Exécute le schéma SQL pour créer les tables."""
    schema_path = Path(__file__).parent.parent / "sql" / "schema.sql"
    
    if not schema_path.exists():
        print(f"✗ Fichier schema.sql non trouvé: {schema_path}")
        return False
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Lire et exécuter le schéma (gestion de l'encodage)
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
        except UnicodeDecodeError:
            # Fallback si UTF-8 échoue
            with open(schema_path, 'r', encoding='latin-1') as f:
                schema_sql = f.read()
        
        # Exécuter chaque commande
        cur.execute(schema_sql)
        conn.commit()
        
        print("✓ Schéma de base de données créé avec succès")
        
        # Vérifier les tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        print(f"✓ Tables créées: {', '.join(tables)}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors de la création du schéma: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


def check_connection():
    """Vérifie la connexion à la base de données."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"✓ Connexion réussie")
        # Gérer l'encodage pour l'affichage de la version
        try:
            version_str = str(version.split(',')[0])
        except (UnicodeDecodeError, UnicodeEncodeError):
            version_str = "PostgreSQL (version non disponible)"
        print(f"  Version PostgreSQL: {version_str}")
        cur.close()
        conn.close()
        return True
    except UnicodeDecodeError as e:
        # Erreur d'encodage - probablement dans le mot de passe ou la configuration
        print(f"✗ Erreur d'encodage lors de la connexion")
        print(f"  Le problème vient probablement du fichier .env")
        print(f"  Vérifiez que le fichier .env est encodé en UTF-8")
        print(f"  Vérifiez aussi que le mot de passe ne contient pas de caractères spéciaux problématiques")
        print(f"  Configuration actuelle:")
        print(f"    DB_NAME={DB_CONFIG['dbname']}")
        print(f"    DB_USER={DB_CONFIG['user']}")
        print(f"    DB_HOST={DB_CONFIG['host']}")
        print(f"    DB_PORT={DB_CONFIG['port']}")
        print(f"    DB_PASSWORD={'*' * len(DB_CONFIG.get('password', '')) if DB_CONFIG.get('password') else '(non défini)'}")
        return False
    except psycopg2.OperationalError as e:
        # Gérer spécifiquement les erreurs de connexion
        try:
            error_msg = str(e)
        except (UnicodeDecodeError, UnicodeEncodeError):
            error_msg = "Erreur de connexion (détails non disponibles - problème d'encodage)"
        print(f"✗ Erreur de connexion: {error_msg}")
        print(f"  Vérifiez votre fichier .env avec:")
        print(f"    DB_NAME={DB_CONFIG['dbname']}")
        print(f"    DB_USER={DB_CONFIG['user']}")
        print(f"    DB_HOST={DB_CONFIG['host']}")
        print(f"    DB_PORT={DB_CONFIG['port']}")
        password_display = '*' * len(DB_CONFIG.get('password', '')) if DB_CONFIG.get('password') else '(non défini)'
        print(f"    DB_PASSWORD={password_display}")
        return False
    except Exception as e:
        # Gérer les autres erreurs
        try:
            error_msg = str(e)
        except (UnicodeDecodeError, UnicodeEncodeError):
            error_msg = "Erreur inconnue (problème d'encodage)"
        print(f"✗ Erreur: {error_msg}")
        return False


def main():
    """Fonction principale."""
    print("="*60)
    print("Configuration de la base de données")
    print("="*60)
    print()
    
    # Vérifier la connexion
    print("1. Vérification de la connexion...")
    if not check_connection():
        return False
    print()
    
    # Vérifier pgvector
    print("2. Vérification de l'extension pgvector...")
    if not check_pgvector():
        print("   Tentative d'activation de l'extension...")
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            print("✓ Extension pgvector activée")
            cur.close()
            conn.close()
        except Exception as e:
            print(f"✗ Impossible d'activer l'extension: {e}")
            print("   Assurez-vous que pgvector est installé sur votre système.")
            return False
    print()
    
    # Créer le schéma
    print("3. Création du schéma de base de données...")
    if not setup_schema():
        return False
    print()
    
    print("="*60)
    print("✓ Configuration terminée avec succès!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

