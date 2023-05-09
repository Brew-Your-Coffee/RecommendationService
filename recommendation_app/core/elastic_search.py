from elasticsearch import Elasticsearch

from RecommendationService.settings import ELASTICSEARCH_HOSTS, ELASTICSEARCH_PASSWORD, ELASTICSEARCH_USERNAME

index_name = 'coffee'


def get_coffees():
    es = get_es()

    search_results = es.search(index=index_name, body={"query": {"match_all": {}}}, size=1000)

    # Extract the coffee data from the search results
    coffee_data = []
    for hit in search_results['hits']['hits']:
        coffee_data.append(hit['_source'])
    return coffee_data


def get_coffee_by_id(coffee_id: str):
    es = get_es()

    search_results = es.get(index=index_name, id=coffee_id)

    return search_results['_source']


def get_es():
    return Elasticsearch(
        ELASTICSEARCH_HOSTS,
        basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
    )
