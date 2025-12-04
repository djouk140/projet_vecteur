"""
Script Python pour télécharger et installer pgvector sur Windows
Nécessite des privilèges administrateur
"""
import os
import sys
import requests
import zipfile
import shutil
from pathlib import Path

def find_postgresql():
    """Trouve l'installation PostgreSQL"""
    versions = ["18", "17", "16", "15", "14"]
    for version in versions:
        pg_path = Path(f"C:/Program Files/PostgreSQL/{version}")
        if pg_path.exists():
            return pg_path, version
    return None, None

def check_admin():
    """Vérifie les privilèges administrateur"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def download_pgvector():
    """Télécharge la dernière version de pgvector"""
    print("Recherche de la dernière version de pgvector...")
    
    try:
        response = requests.get("https://api.github.com/repos/pgvector/pgvector/releases/latest", timeout=10)
        release = response.json()
        version = release.get("tag_name", "unknown")
        print(f"Version trouvée: {version}")
        
        # Chercher un asset Windows
        assets = release.get("assets", [])
        windows_asset = None
        
        for asset in assets:
            name = asset.get("name", "").lower()
            if "windows" in name or "win" in name or name.endswith(".zip"):
                windows_asset = asset
                break
        
        if not windows_asset:
            print("⚠ Aucun binaire Windows précompilé trouvé")
            print("  pgvector doit être compilé depuis les sources")
            print("  Voir: https://github.com/pgvector/pgvector#installation")
            return None, None
        
        print(f"Asset trouvé: {windows_asset['name']}")
        print(f"Taille: {windows_asset['size'] / 1024 / 1024:.2f} MB")
        
        # Télécharger
        download_url = windows_asset["browser_download_url"]
        download_path = Path(os.environ.get("TEMP", ".")) / "pgvector.zip"
        
        print(f"\nTéléchargement depuis: {download_url}")
        print("Cela peut prendre quelques minutes...")
        
        response = requests.get(download_url, stream=True, timeout=30)
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgression: {percent:.1f}%", end='', flush=True)
        
        print("\n✓ Téléchargement terminé")
        return download_path, version
        
    except Exception as e:
        print(f"✗ Erreur lors du téléchargement: {e}")
        return None, None

def install_pgvector(zip_path, pg_path):
    """Installe pgvector depuis le ZIP"""
    print(f"\nExtraction de {zip_path}...")
    
    extract_path = Path(os.environ.get("TEMP", ".")) / "pgvector_extract"
    if extract_path.exists():
        shutil.rmtree(extract_path)
    extract_path.mkdir()
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    print("✓ Extraction terminée")
    
    # Chercher les fichiers
    vector_dll = None
    vector_control = None
    vector_folder = None
    
    for root, dirs, files in os.walk(extract_path):
        for file in files:
            if file == "vector.dll":
                vector_dll = Path(root) / file
            elif file == "vector.control":
                vector_control = Path(root) / file
        
        for dir_name in dirs:
            if dir_name == "vector":
                vector_folder = Path(root) / dir_name
    
    if not vector_dll:
        print("✗ Fichier vector.dll non trouvé dans l'archive")
        print("Structure de l'archive:")
        for root, dirs, files in os.walk(extract_path):
            level = root.replace(str(extract_path), '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:10]:  # Limiter l'affichage
                print(f"{subindent}{file}")
        return False
    
    print("\nInstallation des fichiers...")
    
    # Copier vector.dll
    dll_dest = pg_path / "lib" / "vector.dll"
    try:
        shutil.copy2(vector_dll, dll_dest)
        print(f"✓ vector.dll copié vers: {dll_dest}")
    except PermissionError:
        print(f"✗ Erreur de permission. Copiez manuellement:")
        print(f"  {vector_dll} -> {dll_dest}")
        return False
    
    # Copier vector.control
    if vector_control:
        control_dest = pg_path / "share" / "extension" / "vector.control"
        control_dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(vector_control, control_dest)
            print(f"✓ vector.control copié")
        except PermissionError:
            print(f"✗ Erreur de permission pour vector.control")
    
    # Copier le dossier vector/
    if vector_folder:
        folder_dest = pg_path / "share" / "extension" / "vector"
        if folder_dest.exists():
            shutil.rmtree(folder_dest)
        try:
            shutil.copytree(vector_folder, folder_dest)
            print(f"✓ Dossier vector/ copié")
        except PermissionError:
            print(f"✗ Erreur de permission pour le dossier vector/")
    else:
        # Chercher les fichiers SQL individuellement
        sql_files = list(extract_path.rglob("*.sql"))
        if sql_files:
            folder_dest = pg_path / "share" / "extension" / "vector"
            folder_dest.mkdir(parents=True, exist_ok=True)
            for sql_file in sql_files:
                try:
                    shutil.copy2(sql_file, folder_dest)
                except PermissionError:
                    pass
            print(f"✓ Fichiers SQL copiés")
    
    # Nettoyer
    shutil.rmtree(extract_path)
    zip_path.unlink()
    
    return True

def restart_postgresql(version):
    """Redémarre PostgreSQL"""
    import subprocess
    service_name = f"postgresql-x64-{version}"
    
    print(f"\nRedémarrage de PostgreSQL ({service_name})...")
    try:
        subprocess.run(["net", "stop", service_name], check=True, capture_output=True)
        import time
        time.sleep(2)
        subprocess.run(["net", "start", service_name], check=True, capture_output=True)
        time.sleep(3)
        print("✓ PostgreSQL redémarré")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠ Erreur lors du redémarrage: {e}")
        print("  Redémarrez manuellement PostgreSQL")
        return False

def activate_extension(pg_path, password="root"):
    """Active l'extension pgvector"""
    print("\nActivation de l'extension pgvector...")
    
    psql_path = pg_path / "bin" / "psql.exe"
    if not psql_path.exists():
        print(f"✗ psql.exe non trouvé: {psql_path}")
        return False
    
    import subprocess
    import os
    
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    
    try:
        result = subprocess.run(
            [str(psql_path), "-U", "postgres", "-h", "localhost", "-d", "filmsrec", 
             "-c", "CREATE EXTENSION IF NOT EXISTS vector;"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ Extension pgvector activée avec succès!")
            return True
        else:
            print(f"✗ Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def main():
    print("="*60)
    print("TÉLÉCHARGEMENT ET INSTALLATION DE PGVECTOR")
    print("="*60)
    print()
    
    # Vérifier les privilèges
    if not check_admin():
        print("⚠ Ce script nécessite des privilèges administrateur")
        print("  Relancez en tant qu'administrateur")
        return 1
    
    # Trouver PostgreSQL
    pg_path, pg_version = find_postgresql()
    if not pg_path:
        print("✗ PostgreSQL non trouvé")
        return 1
    
    print(f"✓ PostgreSQL {pg_version} trouvé: {pg_path}")
    
    # Vérifier si déjà installé
    vector_dll = pg_path / "lib" / "vector.dll"
    if vector_dll.exists():
        print(f"✓ pgvector semble déjà installé: {vector_dll}")
        if activate_extension(pg_path):
            return 0
    
    # Télécharger
    zip_path, version = download_pgvector()
    if not zip_path:
        return 1
    
    # Installer
    if not install_pgvector(zip_path, pg_path):
        return 1
    
    # Redémarrer PostgreSQL
    if not restart_postgresql(pg_version):
        print("  Continuez quand même...")
    
    # Activer l'extension
    if activate_extension(pg_path):
        print("\n" + "="*60)
        print("INSTALLATION RÉUSSIE!")
        print("="*60)
        return 0
    else:
        print("\n⚠ Installation terminée mais extension non activée")
        print("  Essayez manuellement:")
        print(f"  {pg_path / 'bin' / 'psql.exe'} -U postgres -d filmsrec -c \"CREATE EXTENSION vector;\"")
        return 1

if __name__ == "__main__":
    sys.exit(main())

