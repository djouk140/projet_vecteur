"""
Script d'évaluation des recommandations.
Rôle 4: Évaluation et rapport
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Set

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_connection_dict
from evaluation.metrics import evaluate_recommendations, evaluate_multiple_queries
import pandas as pd


def load_ground_truth(file_path: str) -> Dict[int, Set[int]]:
    """
    Charge les données de ground truth depuis un fichier JSON.
    
    Format attendu:
    {
        "film_id": [list of relevant film_ids],
        ...
    }
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return {int(k): set(v) for k, v in json.load(f).items()}


def get_recommendations_from_db(film_id: int, k: int = 20) -> List[int]:
    """Récupère les recommandations depuis la base de données."""
    conn, cur = get_connection_dict()
    
    cur.execute("""
        WITH q AS (
            SELECT embedding FROM film_embeddings WHERE film_id = %s
        )
        SELECT f.id
        FROM film_embeddings fe
        JOIN films f ON f.id = fe.film_id
        JOIN q ON TRUE
        WHERE f.id <> %s
        ORDER BY fe.embedding <=> (SELECT embedding FROM q)
        LIMIT %s
    """, (film_id, film_id, k))
    
    results = [row["id"] for row in cur.fetchall()]
    conn.close()
    
    return results


def evaluate_all(ground_truth_path: str, output_path: str = None, k: int = 20):
    """
    Évalue toutes les recommandations avec les données de ground truth.
    
    Args:
        ground_truth_path: Chemin vers le fichier JSON de ground truth
        output_path: Chemin pour sauvegarder les résultats (optionnel)
        k: Nombre de recommandations à évaluer
    """
    print(f"Chargement du ground truth: {ground_truth_path}")
    ground_truth = load_ground_truth(ground_truth_path)
    
    print(f"Nombre de films à évaluer: {len(ground_truth)}")
    
    evaluations = []
    k_values = [5, 10, 20]
    
    for query_film_id, relevant_films in ground_truth.items():
        print(f"Évaluation du film {query_film_id}...")
        
        recommended = get_recommendations_from_db(query_film_id, k=max(k_values))
        
        eval_data = {
            "query_film_id": query_film_id,
            "recommended_film_ids": recommended,
            "ground_truth_relevant": relevant_films
        }
        
        evaluations.append(eval_data)
    
    # Calcul des métriques moyennes
    print("\nCalcul des métriques...")
    avg_metrics = evaluate_multiple_queries(evaluations, k_values)
    
    # Affichage des résultats
    print("\n" + "="*60)
    print("RÉSULTATS D'ÉVALUATION")
    print("="*60)
    
    for metric, value in sorted(avg_metrics.items()):
        print(f"{metric}: {value:.4f}")
    
    # Sauvegarde des résultats
    if output_path:
        results = {
            "average_metrics": avg_metrics,
            "individual_evaluations": [
                {
                    "query_film_id": e["query_film_id"],
                    "metrics": evaluate_recommendations(
                        e["query_film_id"],
                        e["recommended_film_ids"],
                        e["ground_truth_relevant"],
                        k_values
                    )
                }
                for e in evaluations
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nRésultats sauvegardés dans: {output_path}")
    
    return avg_metrics


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Évaluer les recommandations")
    parser.add_argument("ground_truth", help="Fichier JSON avec le ground truth")
    parser.add_argument("--output", "-o", help="Fichier de sortie pour les résultats")
    parser.add_argument("--k", type=int, default=20, help="Nombre de recommandations à évaluer")
    
    args = parser.parse_args()
    
    evaluate_all(args.ground_truth, args.output, args.k)

