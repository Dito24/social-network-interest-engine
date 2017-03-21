import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.linked_data import get_ontology_data

if __name__ == "__main__":
    for item in get_ontology_data('manchester united reserves'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()

    for item in get_ontology_data('Donald Trump'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()

    for item in get_ontology_data('jurassic park'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()

    for item in get_ontology_data('European Organization for Nuclear Research'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()

    for item in get_ontology_data('Facebook'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()

    for item in get_ontology_data('Ebola'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()

    for item in get_ontology_data('Joe Biden'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()

    for item in get_ontology_data('John Legend'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()

    for item in get_ontology_data('Walmart'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()

    for item in get_ontology_data('hawking'):
        print(item['name'])
        print(item['details'])
        print(item['score'])
        print()
