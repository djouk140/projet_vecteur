"""
Script pour diagnostiquer et corriger les problèmes d'encodage du fichier .env
"""
import os
from pathlib import Path

def check_env_file():
    """Vérifie et corrige le fichier .env"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("✗ Le fichier .env n'existe pas")
        print("  Créez-le à partir de env_example.txt")
        return False
    
    print("Vérification du fichier .env...")
    
    # Essayer de lire avec différents encodages
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    content = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(env_path, 'r', encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            print(f"✓ Fichier lu avec succès en {encoding}")
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print("✗ Impossible de lire le fichier .env avec les encodages testés")
        return False
    
    # Afficher les variables (masquer le mot de passe)
    lines = content.split('\n')
    print("\nVariables détectées:")
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            if 'PASSWORD' in key.upper():
                print(f"  {key}=***")
            else:
                print(f"  {key}={value}")
    
    # Proposer de créer une version UTF-8
    if used_encoding != 'utf-8':
        print(f"\n⚠ Le fichier est encodé en {used_encoding}, pas en UTF-8")
        print("  Création d'une copie en UTF-8...")
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✓ Fichier .env converti en UTF-8")
        except Exception as e:
            print(f"✗ Erreur lors de la conversion: {e}")
            return False
    
    return True

if __name__ == "__main__":
    check_env_file()

