import json
import os
import re
import sys

import requests
from retrying import retry
from urllib.error import HTTPError

import pyld
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
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

    request = requests.get(
        "https://kgsearch.googleapis.com/v1/entities:search", params=dict(query=keyword, key=kg_key, limit=3))

    json_ld = json.loads(request.text)

    normalized = pyld.jsonld.normalize(json_ld, {'algorithm': 'URDNA2015', 'format': 'application/nquads'})

    g = rdflib.Graph()
    g.parse(data=normalized, format='n3')
    g.serialize(format='turtle')

    q = """SELECT ?name ?description ?detail ?score
    WHERE
    {
    ?entity a ns2:EntitySearchResult ; ns2:resultScore ?score ; ns1:result ?result .
    ?result ns1:name ?name .
    OPTIONAL
    {
    ?result ns1:description ?description .
    }
    OPTIONAL
    {
    ?result ns2:detailedDescription ?detailed .
    ?detailed ns1:articleBody ?detail .
    }
    }
    ORDER BY DESC(?score)
    """

    result = None
    try:
        result = g.query(q).serialize(format='csv')
    except Exception:
        pass

    return result


def refine_knowledge_graph_result(result):
    if result is None:
        return []

    rows = re.split('\r', result.decode("utf-8"))

    # discard first row of headers
    rows = rows[1:]

    # strip string newline characters
    for index in range(len(rows)):
        rows[index] = (rows[index].replace('\n', '').replace('"', ''))

    # if the first row is empty
    if not rows[0]:
        return []

    return rows


def get_ontology_data(keyword):
    # to avoid randomly generated empty results
    attempts = 0
    result = []
    while attempts < 3 and not result:
        result = refine_knowledge_graph_result(get_knowledge_graph_result(keyword))
        attempts += 1

    # if the result set for keyword is empty
    if not result:
        return []

    # split the result set data
    entities = []
    for line in result:
        if not line:
            continue

        line = line.strip()
        results = line.split(',', 1)
        if len(results) < 2:
            continue

        results.extend(results[1].split(',', 1))
        del results[1]

        if len(results) < 3:
            continue

        results.extend(results[2].rsplit(',', 1))
        del results[2]

        try:
            types = get_ontology_types(results[0])
        except Exception:
            types = []

        results.append(list(set(types) - {results[1].title()}))

        entities.append(results)

    index = 0
    result = None
    for entity in entities:
        if index > 0:
            diff = result - float(entity[3])

            if diff > 100:
                break

        result = float(entity[3])
        index += 1

    return entities[:index]

if __name__ == "__main__":
    # print(str(get_ontology_types('Manchester United F.C.')))

    # print(str(get_knowledge_graph_result('Manchester United')))

    # print(get_ontology_data('manchester united'))
    # print()
    # print(get_ontology_data('kusal'))

    print(get_ontology_types('Manchester United F.C.'))
