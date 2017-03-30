import json
import os
import re
import sys
from urllib.error import HTTPError

import requests
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from retrying import retry

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from text_analysis.text_analytics import calculate_word_similarity
from text_analysis.text_refinement import camel_case_split


def load_type_dictionary(file_path):
    if file_path is None:
        return None

    content = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if line is not None:
                    components = line.split(':')
                    values = components[1].split(',')
                    values = [match.rstrip() for match in values]

                    content[components[0]] = values

    return content


DOMAIN_DICT = load_type_dictionary(os.environ['INTEREST_ENGINE_PATH'] + '/social_networks/data/domains.txt')
TYPE_SYNONYM_DICT = load_type_dictionary(os.environ['INTEREST_ENGINE_PATH'] + '/social_networks/data/types.txt')
TYPE_PATTERN_DICT = load_type_dictionary(os.environ['INTEREST_ENGINE_PATH'] + '/social_networks/data/type_patterns.txt')
GENERIC_CLASSES = ['Activity', 'Agent', 'Person', 'Work', 'Unknown']


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


def get_ontology_super_classes(subclass):
    if subclass is None:
        return None

    superclass = subclass
    hierarchy = []
    while superclass is not None:
        hierarchy.insert(0, superclass)
        superclass = get_ontology_super_class(superclass)

    hierarchy.insert(0, 'Thing')
    return hierarchy


def get_knowledge_graph_result(keyword):
    # improve mechanism to retrieve the key
    kg_key = os.environ['GOOGLE_KNOWLEDGE_GRAPH_KEY']

    response = requests.get(
        "https://kgsearch.googleapis.com/v1/entities:search", params=dict(query=keyword, key=kg_key, limit=3))
    json_ld = json.loads(response.text)

    entities = []
    if 'itemListElement' not in json_ld:
        return entities

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
            types = sort_class_order(get_ontology_types(title))
        except (Exception, KeyError):
            types = []

        # description of the entity
        try:
            description = str(element['result']['description'])
        except KeyError:
            description = None

        # improving the ontology class discovery in combination with Google Knowledge graph data
        if not types or types[len(types) - 1] in GENERIC_CLASSES and description is not None:
            match = match_type_through_description(description)
            if match is None:
                match = match_type_through_description_pattern(description)
            if match is not None:
                try:
                    types = get_ontology_super_classes(match)
                except (Exception, KeyError):
                    types = []

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

        if similarity is None:
            similarity = 0

        if relevance_as_ratio is None:
            relevance_as_ratio = 0

        weighted_score = ((relevance_as_ratio * knowledge_weight) +
                          (similarity * textual_weight)) / (knowledge_weight + textual_weight)

        entity['score'] = weighted_score

    entities = sorted(entities, key=lambda k: k['score'], reverse=True)

    previous_score = 0
    index = 0
    for entity in entities:
        if previous_score != 0:
            if (previous_score / entity['score']) > 1.5:
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


def sort_class_order(types):
    if types is None:
        return None

    if not types:
        return []

    ordered = []

    child_parent = {}
    for class_type in types:
        try:
            super_class = get_ontology_super_class(class_type)
            child_parent[class_type] = super_class
        except Exception:
            return ordered

    parent = return_key(child_parent, None)
    ordered.append(parent)
    while parent is not None:
        parent = return_key(child_parent, parent)
        if parent is not None:
            ordered.append(parent)

    return ordered


def return_key(dictionary, value):
    matching = {child: parent for child, parent in dictionary.items() if parent == value}
    matching_value = None

    for child, parent in matching.items():
        matching_value = child

    return matching_value


def match_type_through_description(description):
    if description is None:
        return None

    for type_class, synonyms in TYPE_SYNONYM_DICT.items():
        for item in synonyms:
            if item == description.lower():
                return type_class

    return None


def match_type_through_description_pattern(description):
    if description is None:
        return None

    for type_class, pattern_strings in TYPE_PATTERN_DICT.items():
        for item in pattern_strings:
            pattern = re.compile(item)
            if pattern.search(description.lower()):
                return type_class

    return None


def match_type_domain(sub_type):
    if sub_type is None:
        return None

    for domain, types in DOMAIN_DICT.items():
        if sub_type in types:
            return domain

    return None


def get_tag_domains(tags):
    if tags is None:
        return None

    domains = []
    for tag in tags:
        types = tag.context['sub_types']
        types = [sub_type for sub_type in types if sub_type is not None]

        index = len(types) - 1
        domain = None
        while domain is None and index >= 0:
            domain = match_type_domain(types[index])
            index -= 1

        if domain is not None:
            domains.append(domain)

    return domains


if __name__ == "__main__":
    # for term in get_ontology_data('Donald Trump'):
    #     print(term['name'])
    #     print(term['types'])
    #     print(term['description'])
    #     print()
    # pattern = re.compile('[\w]* president')
    # string = '45th U.S. President'.lower()

    print(DOMAIN_DICT)

    # print(pattern.search(string))
