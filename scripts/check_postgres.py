"""
Script pour vérifier l'état de PostgreSQL
"""
import socket
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", "5432"))

print(f"Vérification de PostgreSQL sur {host}:{port}...")

# Vérifier si le port est ouvert
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        print(f"✓ Le port {port} est ouvert (PostgreSQL est probablement démarré)")
    else:
        print(f"✗ Le port {port} est fermé (PostgreSQL n'est probablement pas démarré)")
        print("  Démarrez PostgreSQL avec:")
        print("    - Windows: net start postgresql-x64-XX (remplacez XX par votre version)")
        print("    - Ou via les Services Windows")
except Exception as e:
    print(f"✗ Erreur lors de la vérification: {e}")

