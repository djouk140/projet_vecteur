"""
Métriques d'évaluation pour les recommandations.
Rôle 4: Évaluation et rapport
"""
import numpy as np
from typing import List, Dict, Set


def precision_at_k(relevant_items: Set[int], recommended_items: List[int], k: int) -> float:
    """
    Calcule Precision@K.
    
    Args:
        relevant_items: Ensemble des items pertinents
        recommended_items: Liste ordonnée des items recommandés
        k: Nombre de résultats à considérer
    
    Returns:
        Precision@K (0.0 à 1.0)
    """
    if k == 0 or len(recommended_items) == 0:
        return 0.0
    
    top_k = recommended_items[:k]
    relevant_in_top_k = sum(1 for item in top_k if item in relevant_items)
    return relevant_in_top_k / min(k, len(top_k))


def recall_at_k(relevant_items: Set[int], recommended_items: List[int], k: int) -> float:
    """
    Calcule Recall@K.
    
    Args:
        relevant_items: Ensemble des items pertinents
        recommended_items: Liste ordonnée des items recommandés
        k: Nombre de résultats à considérer
    
    Returns:
        Recall@K (0.0 à 1.0)
    """
    if len(relevant_items) == 0:
        return 0.0
    
    top_k = recommended_items[:k]
    relevant_in_top_k = sum(1 for item in top_k if item in relevant_items)
    return relevant_in_top_k / len(relevant_items)


def ndcg_at_k(relevant_items: Set[int], recommended_items: List[int], k: int) -> float:
    """
    Calcule nDCG@K (Normalized Discounted Cumulative Gain).
    
    Args:
        relevant_items: Ensemble des items pertinents (non ordonnés)
        recommended_items: Liste ordonnée des items recommandés
        k: Nombre de résultats à considérer
    
    Returns:
        nDCG@K (0.0 à 1.0)
    """
    if len(relevant_items) == 0 or k == 0:
        return 0.0
    
    top_k = recommended_items[:k]
    
    # Calcul du DCG
    dcg = 0.0
    for i, item in enumerate(top_k, 1):
        if item in relevant_items:
            # Gain = 1 si pertinent, 0 sinon
            gain = 1.0
            dcg += gain / np.log2(i + 1)
    
    # Calcul du IDCG (meilleur cas possible)
    idcg = 0.0
    num_relevant = min(len(relevant_items), k)
    for i in range(1, num_relevant + 1):
        idcg += 1.0 / np.log2(i + 1)
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def mean_average_precision(relevant_items: Set[int], recommended_items: List[int], k: int = None) -> float:
    """
    Calcule Mean Average Precision (MAP).
    
    Args:
        relevant_items: Ensemble des items pertinents
        recommended_items: Liste ordonnée des items recommandés
        k: Nombre maximum de résultats à considérer (None = tous)
    
    Returns:
        MAP (0.0 à 1.0)
    """
    if len(relevant_items) == 0:
        return 0.0
    
    if k is not None:
        recommended_items = recommended_items[:k]
    
    precisions = []
    relevant_found = 0
    
    for i, item in enumerate(recommended_items, 1):
        if item in relevant_items:
            relevant_found += 1
            precisions.append(relevant_found / i)
    
    if len(precisions) == 0:
        return 0.0
    
    return np.mean(precisions)


def evaluate_recommendations(
    query_film_id: int,
    recommended_film_ids: List[int],
    ground_truth_relevant: Set[int],
    k_values: List[int] = [5, 10, 20]
) -> Dict[str, float]:
    """
    Évalue les recommandations avec plusieurs métriques.
    
    Args:
        query_film_id: ID du film de requête
        recommended_film_ids: Liste ordonnée des IDs recommandés
        ground_truth_relevant: Ensemble des IDs pertinents
        k_values: Liste des valeurs K à évaluer
    
    Returns:
        Dictionnaire avec toutes les métriques
    """
    results = {}
    
    for k in k_values:
        results[f"precision@{k}"] = precision_at_k(ground_truth_relevant, recommended_film_ids, k)
        results[f"recall@{k}"] = recall_at_k(ground_truth_relevant, recommended_film_ids, k)
        results[f"ndcg@{k}"] = ndcg_at_k(ground_truth_relevant, recommended_film_ids, k)
    
    results["map"] = mean_average_precision(ground_truth_relevant, recommended_film_ids)
    
    return results


def evaluate_multiple_queries(
    evaluations: List[Dict],
    k_values: List[int] = [5, 10, 20]
) -> Dict[str, float]:
    """
    Évalue plusieurs requêtes et retourne les métriques moyennes.
    
    Args:
        evaluations: Liste de dictionnaires avec les clés:
            - query_film_id
            - recommended_film_ids
            - ground_truth_relevant
        k_values: Liste des valeurs K à évaluer
    
    Returns:
        Dictionnaire avec les métriques moyennes
    """
    if len(evaluations) == 0:
        return {}
    
    all_results = []
    for eval_data in evaluations:
        results = evaluate_recommendations(
            eval_data["query_film_id"],
            eval_data["recommended_film_ids"],
            eval_data["ground_truth_relevant"],
            k_values
        )
        all_results.append(results)
    
    # Moyennes
    avg_results = {}
    for metric in all_results[0].keys():
        values = [r[metric] for r in all_results]
        avg_results[f"mean_{metric}"] = np.mean(values)
        avg_results[f"std_{metric}"] = np.std(values)
    
    return avg_results

