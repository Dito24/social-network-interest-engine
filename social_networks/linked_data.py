import json
import os
import sys

import requests
from retrying import retry
from urllib.error import HTTPError

from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from text_analysis.text_analytics import calculate_word_similarity
from text_analysis.text_refinement import camel_case_split


@retry(wait_exponential_multiplier=1000, wait_exponential_max=20000, stop_max_delay=120000)
def get_ontology_types(subject):
    if subject is None:
        return None

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?labels
        WHERE {
            ?person rdfs:label "%s"@en ; rdf:type ?labels
            FILTER (strstarts(str(?labels), "http://dbpedia.org/ontology/"))
        }
    """ % subject)

    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
    except (HTTPError, SPARQLExceptions.EndPointInternalError,
            SPARQLExceptions.EndPointNotFound, SPARQLExceptions.QueryBadFormed):
        raise Exception("Retry!")

    types = []
    if results:
        for result in results["results"]["bindings"]:
            words = camel_case_split((result["labels"]["value"]).replace("http://dbpedia.org/ontology/", ""))
            split = " ".join(words)
            types.append(split.lower().title())

    types = [ontology_type for ontology_type in types if 'Wikidata' not in ontology_type]

    return types


@retry(wait_exponential_multiplier=1000, wait_exponential_max=20000, stop_max_delay=120000)
def get_ontology_super_class(subclass):
    if not subclass:
        return None

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?superclass
            WHERE {
            dbo:%s rdfs:subClassOf ?superclass
            FILTER (strstarts(str(?superclass), "http://dbpedia.org/ontology/"))
            }
        """ % subclass.replace(" ", ""))

    sparql.setReturnFormat(JSON)
    try:
        results = sparql.query().convert()
    except (HTTPError, SPARQLExceptions.EndPointInternalError,
            SPARQLExceptions.EndPointNotFound, SPARQLExceptions.QueryBadFormed):
        raise Exception("Retry!")

    try:
        if 'results' in locals():
            values = camel_case_split((results["results"]["bindings"][0]["superclass"]["value"])
                                      .replace("http://dbpedia.org/ontology/", ""))
            return ' '.join(values)
        else:
            return None
    except (IndexError, TypeError):
        return None


def get_knowledge_graph_result(keyword):
    # improve mechanism to retrieve the key
    kg_key = os.environ['GOOGLE_KNOWLEDGE_GRAPH_KEY']

    response = requests.get(
        "https://kgsearch.googleapis.com/v1/entities:search", params=dict(query=keyword, key=kg_key, limit=3))
    json_ld = json.loads(response.text)

    entities = []
    previous_score = -1
    sum_of_scores = 0

    for element in json_ld['itemListElement']:
        # name of the entity
        try:
            title = element['result']['name']
        except KeyError:
            title = None

        # entity types
        try:
            # get schema.org ontology types
            # types = [n for n in element['result']['@type']]

            # get DBpedia ontology types
            types = get_ontology_types(title)
        except KeyError:
            types = []

        # description of the entity
        try:
            description = str(element['result']['description'])
        except KeyError:
            description = None

        # detailed description of the entity
        try:
            detail_desc = element['result']['detailedDescription']['articleBody']
        except KeyError:
            detail_desc = None

        try:
            score = element['resultScore']
        except KeyError:
            score = 0

        if previous_score > 0 and (score - previous_score) > 100:
            break

        previous_score = score
        sum_of_scores += score

        entities.append({
            'name': title, 'types': types, 'description': description,
            'details': detail_desc, 'score': score
        })

    # prioritize the results based on semantics and text similarity
    for entity in entities:
        relevance = entity['score']

        relevance_as_ratio = relevance / sum_of_scores
        similarity = calculate_word_similarity(keyword, entity['name'])

        knowledge_weight = 0.7
        textual_weight = 0.3

        weighted_score = ((relevance_as_ratio * knowledge_weight) +
                          (similarity * textual_weight)) / (knowledge_weight + textual_weight)

        entity['score'] = weighted_score

    entities = sorted(entities, key=lambda k: k['score'], reverse=True)

    previous_score = 0
    index = 0
    for entity in entities:
        if previous_score != 0:
            if (previous_score / entity['score']) > 2:
                break

        previous_score = entity['score']
        index += 1

    return entities[:index]


def get_ontology_data(keyword):
    # to avoid randomly generated empty results
    attempts = 0
    result = []
    while attempts < 3 and not result:
        result = get_knowledge_graph_result(keyword)
        attempts += 1

    return result


if __name__ == "__main__":
    for item in get_ontology_data('manchester united reserves and academy'):
        print(item['name'])
        print(item['types'])
        print(item['score'])
        print()

    for item in get_ontology_data('European Organization for Nuclear Research'):
        print(item['name'])
        print(item['types'])
        print(item['score'])
        print()
