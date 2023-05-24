from typing import Dict

import numpy as np
from sklearn.cluster import AffinityPropagation

from recommendation_app.core.elastic_search import get_coffees
from recommendation_app.core.postgres import get_likes


# Define the similarity metric function
def similarity(coffee1, coffee2):
    taste_similarity = get_tastes_similarity(coffee1, coffee2)
    processing_method_similarity = get_param_similarity(coffee1, coffee2, "processingMethod")
    origin_similarity = get_param_similarity(coffee1, coffee2, "country")
    return taste_similarity + processing_method_similarity + origin_similarity


def get_tastes_similarity(coffee1, coffee2):
    tastes1 = set(coffee1["tastes"])
    tastes2 = set(coffee2["tastes"])

    return - len(tastes1.union(tastes2)) + len(tastes1.intersection(tastes2))


def get_param_similarity(coffee1, coffee2, param):
    value1 = coffee1.get(param, None)
    if value1 is None:
        return -2
    value2 = coffee2.get(param, None)
    if value2 is None:
        return -2
    return 0 if value1 == value2 else -2


def create_similarity_matrix():
    coffee_data = get_coffees()
    # Create a similarity matrix
    n_coffees = len(coffee_data)
    similarity_matrix = np.zeros((n_coffees, n_coffees))
    id_to_pos = {}
    min_value = 0
    for i, coffee1 in enumerate(coffee_data):
        id_to_pos[coffee1["id"]] = i
        for j, coffee2 in enumerate(coffee_data):
            if i == j:
                continue
            similarity_matrix[i, j] = similarity(coffee1, coffee2)
            min_value = min(similarity_matrix[i, j], min_value)

    for i in range(n_coffees):
        assert similarity_matrix[i, i] == 0, f"{similarity_matrix[i, i]}"
        similarity_matrix[i, i] = min_value * 2
    return similarity_matrix, id_to_pos


def get_affinity_propagation():
    similarity_matrix, id_to_pos = create_similarity_matrix()
    # Run the affinity propagation algorithm
    affprop = AffinityPropagation(damping=0.5, max_iter=2000, affinity='precomputed')
    affprop.fit(similarity_matrix)
    return affprop, id_to_pos


def coffee_recommendations_by_user(user_id, affprop, id_to_pos):
    # get all clusters for past likes
    past_likes = get_likes(user_id)

    clusters_dict = {}
    for coffee_id in past_likes:
        cur_coffee_cluster = affprop.labels_[id_to_pos[coffee_id]]
        if cur_coffee_cluster in clusters_dict:
            clusters_dict[cur_coffee_cluster].append(coffee_id)
        else:
            clusters_dict[cur_coffee_cluster] = [coffee_id]

    clusters_size_list = []
    for cluster in clusters_dict:
        clusters_size_list.append((len(clusters_dict[cluster]), cluster))

    clusters_size_list = sorted(clusters_size_list, reverse=True)

    # get recommendations
    MAX_SIZE = 10
    coffee_data = get_coffees()
    recommended_coffee_list = []
    preferred_cluster_list = []
    for _, preferred_cluster in clusters_size_list:
        preferred_cluster_list.append(preferred_cluster)
        for coffee_item in coffee_data:
            cur_coffee_pos = id_to_pos[coffee_item["id"]]
            if affprop.labels_[cur_coffee_pos] == preferred_cluster: # and coffee_item["id"] not in clusters_dict[preferred_cluster]:
                recommended_coffee_list.append(coffee_item)
            if len(recommended_coffee_list) >= MAX_SIZE:
                break
        if len(recommended_coffee_list) >= MAX_SIZE:
            break

    return sorted(recommended_coffee_list, key=lambda entry: entry["enabled"], reverse=True), preferred_cluster_list


def coffee_recommendations_by_coffee(input_coffee_id: str, affprop: AffinityPropagation, id_to_pos: Dict[str, int]):
    coffee_data = get_coffees()

    input_coffee_pos = id_to_pos[input_coffee_id]
    preferred_cluster = affprop.labels_[input_coffee_pos]

    recommended_coffee_list = []
    for coffee in coffee_data:
        cur_coffee_pos = id_to_pos[coffee["id"]]
        if affprop.labels_[cur_coffee_pos] == preferred_cluster and cur_coffee_pos != input_coffee_pos:
            recommended_coffee_list.append(coffee)

    return sorted(recommended_coffee_list, key=lambda entry: entry["enabled"], reverse=True)[:5], preferred_cluster
