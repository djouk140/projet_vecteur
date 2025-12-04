"""Vérifie les releases disponibles de pgvector"""
import requests

try:
    r = requests.get('https://api.github.com/repos/pgvector/pgvector/releases/latest', timeout=10)
    data = r.json()
    print(f"Version: {data['tag_name']}")
    print(f"\nAssets disponibles:")
    for asset in data['assets']:
        size_mb = asset['size'] / 1024 / 1024
        print(f"  - {asset['name']} ({size_mb:.1f} MB)")
        if 'windows' in asset['name'].lower() or 'win' in asset['name'].lower():
            print(f"    -> {asset['browser_download_url']}")
except Exception as e:
    print(f"Erreur: {e}")

