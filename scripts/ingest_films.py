"""
Script d'ingestion des films depuis un fichier CSV.
Rôle 1: Données et ingestion
"""
import pandas as pd
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_connection
from psycopg2.extras import execute_values

def clean_genres(genres_str):
    """Nettoie et formate les genres."""
    if pd.isna(genres_str) or genres_str == "":
        return []
    # Supporte plusieurs formats: "|", ",", ";"
    for sep in ["|", ",", ";"]:
        if sep in str(genres_str):
            return [g.strip() for g in str(genres_str).split(sep) if g.strip()]
    return [str(genres_str).strip()] if str(genres_str).strip() else []


def clean_cast(cast_str):
    """Nettoie et formate le cast."""
    if pd.isna(cast_str) or cast_str == "":
        return []
    for sep in ["|", ",", ";"]:
        if sep in str(cast_str):
            return [c.strip() for c in str(cast_str).split(sep) if c.strip()]
    return [str(cast_str).strip()] if str(cast_str).strip() else []


def ingest_from_csv(csv_path, batch_size=1000):
    """
    Ingère les films depuis un fichier CSV.
    
    Format CSV attendu (colonnes):
    - title: titre du film (obligatoire)
    - year: année de sortie
    - genres: genres séparés par |, , ou ;
    - cast: acteurs séparés par |, , ou ;
    - synopsis: description du film
    - meta: JSON optionnel avec métadonnées
    
    Args:
        csv_path: chemin vers le fichier CSV
        batch_size: taille des lots pour l'insertion
    """
    print(f"Lecture du fichier CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"Nombre de lignes dans le CSV: {len(df)}")
    
    # Vérification des colonnes requises
    required_cols = ["title"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colonnes manquantes dans le CSV: {missing_cols}")
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Préparer les données
    rows = []
    duplicates = 0
    
    for idx, row in df.iterrows():
        title = str(row["title"]).strip() if pd.notna(row["title"]) else None
        if not title:
            continue
            
        year = int(row["year"]) if pd.notna(row.get("year")) and str(row["year"]).isdigit() else None
        genres = clean_genres(row.get("genres"))
        cast = clean_cast(row.get("cast"))
        synopsis = str(row["synopsis"]).strip() if pd.notna(row.get("synopsis")) else None
        
        # Gestion du champ meta (JSON)
        meta = None
        if "meta" in row and pd.notna(row["meta"]):
            try:
                import json
                if isinstance(row["meta"], str):
                    meta = json.loads(row["meta"])
                else:
                    meta = row["meta"]
            except:
                meta = None
        
        rows.append((title, year, genres, cast, synopsis, meta))
    
    print(f"Nombre de films à insérer: {len(rows)}")
    
    # Insertion par lots
    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        try:
            execute_values(
                cur,
                """
                INSERT INTO films (title, year, genres, cast, synopsis, meta)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                batch,
                template=None,
                page_size=batch_size
            )
            inserted += cur.rowcount
            print(f"Lot {i//batch_size + 1}: {cur.rowcount} films insérés")
        except Exception as e:
            print(f"Erreur lors de l'insertion du lot {i//batch_size + 1}: {e}")
            conn.rollback()
            continue
    
    conn.commit()
    print(f"Total de films insérés: {inserted}")
    
    # Statistiques
    cur.execute("SELECT COUNT(*) FROM films")
    total = cur.fetchone()[0]
    print(f"Total de films dans la base: {total}")
    
    cur.close()
    conn.close()
    print("Ingestion terminée avec succès!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingérer des films depuis un CSV")
    parser.add_argument("csv_path", help="Chemin vers le fichier CSV")
    parser.add_argument("--batch-size", type=int, default=1000, help="Taille des lots")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_path):
        print(f"Erreur: Le fichier {args.csv_path} n'existe pas.")
        sys.exit(1)
    
    ingest_from_csv(args.csv_path, args.batch_size)

