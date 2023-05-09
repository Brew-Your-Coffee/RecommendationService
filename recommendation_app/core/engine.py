from typing import Dict

import numpy as np
from sklearn.cluster import AffinityPropagation

from recommendation_app.core.elastic_search import get_coffees


# Define the similarity metric function
def similarity(coffee1, coffee2):
    taste_similarity = get_tastes_similarity(coffee1, coffee2)
    processing_method_similarity = get_param_similarity(coffee1, coffee2, "processingMethod")
    origin_similarity = get_param_similarity(coffee1, coffee2, "country")
    return taste_similarity + processing_method_similarity + origin_similarity


def get_tastes_similarity(coffee1, coffee2):
    tastes1 = set(coffee1["tastes"])
    tastes2 = set(coffee2["tastes"])

    return len(tastes1.intersection(tastes2))


def get_param_similarity(coffee1, coffee2, param):
    value1 = coffee1.get(param, None)
    if value1 is None:
        return 0
    value2 = coffee2.get(param, None)
    if value2 is None:
        return 0
    return 1 if value1 == value2 else 0


def create_similarity_matrix():
    coffee_data = get_coffees()
    # Create a similarity matrix
    n_coffees = len(coffee_data)
    similarity_matrix = np.zeros((n_coffees, n_coffees))
    id_to_pos = {}
    for i, coffee1 in enumerate(coffee_data):
        id_to_pos[coffee1["id"]] = i
        for j, coffee2 in enumerate(coffee_data):
            similarity_matrix[i, j] = similarity(coffee1, coffee2)
    return similarity_matrix, id_to_pos


def get_affinity_propagation():
    similarity_matrix, id_to_pos = create_similarity_matrix()
    # Run the affinity propagation algorithm
    affprop = AffinityPropagation(damping=0.5, max_iter=200, affinity='precomputed')
    affprop.fit(similarity_matrix)
    return affprop, id_to_pos


def coffee_recommendations_by_user(user_id, affprop, id_to_pos):
    coffee_data = get_coffees()
    past_likes = []

    # Identify the cluster containing the user's preferred coffee types
    labels = affprop.labels_
    preferred_cluster = None
    for i, cluster_center in enumerate(affprop.cluster_centers_indices_):
        if list(coffee_data.keys())[cluster_center] in past_likes:
            preferred_cluster = i
            break

    # Return the coffee types in the preferred cluster that are most similar to the user's preferred coffee types
    recommended_coffees = []
    for i, coffee in enumerate(coffee_data):
        if labels[i] == preferred_cluster and coffee not in past_likes:
            recommended_coffees.append(coffee)

    return recommended_coffees.sort(key=lambda entry: entry.enabled, reverse=True)


def coffee_recommendations_by_coffee(input_coffee_id: str, affprop: AffinityPropagation, id_to_pos: Dict[str, int]):
    coffee_data = get_coffees()

    input_coffee_pos = id_to_pos[input_coffee_id]
    preferred_cluster = affprop.labels_[input_coffee_pos]

    recommended_coffee_list = []
    for coffee in coffee_data:
        cur_coffee_pos = id_to_pos[coffee["id"]]
        if affprop.labels_[cur_coffee_pos] == preferred_cluster and cur_coffee_pos != input_coffee_pos:
            recommended_coffee_list.append(coffee)

    return sorted(recommended_coffee_list, key=lambda entry: entry["enabled"], reverse=True), preferred_cluster
