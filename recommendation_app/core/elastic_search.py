from elasticsearch import Elasticsearch

from RecommendationService.settings import ELASTICSEARCH_HOSTS, ELASTICSEARCH_PASSWORD, ELASTICSEARCH_USERNAME

index_name = 'coffee'
min_score = 0.5


def get_coffees():
    es = get_es()

    search_results = es.search(index=index_name, body={"query": {"match_all": {}}}, size=1000)

    # Extract the coffee data from the search results
    coffee_data = []
    for hit in search_results['hits']['hits']:
        coffee_data.append(hit['_source'])
    return coffee_data


def get_coffees_with_pagination(limit: int, offset: int):
    es = get_es()

    search_results = es.search(index=index_name, body={"query": {"match_all": {}}, "sort": [
        {
            "enabled": "desc"
        }
    ]}, size=limit, from_=offset)

    # Extract the coffee data from the search results
    coffee_data = []
    for hit in search_results['hits']['hits']:
        coffee_data.append(hit['_source'])
    return coffee_data, search_results['hits']['total']['value']


def get_coffees_by_search_str(search: str, limit: int, offset: int):
    es = get_es()

    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "title": {
                                "query": search,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    {
                        "match": {
                            "country": {
                                "query": search,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    {
                        "match": {
                            "tastes": {
                                "query": search,
                                "fuzziness": "AUTO"
                            }
                        }
                    },
                    {
                        "match": {
                            "description": {
                                "query": search,
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                ]
            },
        },
        "sort": [
            {
                "enabled": "desc"
            }
        ]
    }

    search_results = es.search(index=index_name, body=query, size=limit, from_=offset, min_score=min_score)

    # Extract the coffee data from the search results
    coffee_data = []
    for hit in search_results['hits']['hits']:
        coffee_data.append(hit['_source'])
    return coffee_data, search_results['hits']['total']['value']


def get_coffee_by_id(coffee_id: str):
    es = get_es()

    print(coffee_id)
    search_results = es.get(index=index_name, id=coffee_id)

    return search_results['_source']


def get_es():
    return Elasticsearch(
        ELASTICSEARCH_HOSTS,
        basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD)
    )
