import os
import re
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.concepts import Tag
from social_networks.linked_data import get_ontology_data
from text_analysis.text_analytics import extract_entities, get_entity_fractions


def get_named_entity_tags(text):
    entities = extract_entities(text)
    entities = get_entity_fractions(entities, text)

    tags = []
    for entity in entities:
        data = get_ontology_data(entity['entity'])

        if not data:
            data = get_ontology_data(entity['entity'])

        for datum in data:
            # context = {'type': datum[1], 'description': datum[2], 'sub_types': datum[4]}

            context = {'type': datum[1], 'description': datum[2]}

            tag = Tag(datum[0], context, context_fraction=entity['fraction'])
            if tag not in tags:
                tags.append(tag)

    return tags


def load_latest_status_ids():
    # TODO: change the file storage to database
    file_name = "ids.txt"
    file_path = os.path.realpath('.') + '/content/' + file_name

    ids = dict()

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if ":" in line:
                    content = re.split('[:]', line)
                    ids[content[0]] = content[1].strip('\n')

    return ids


def update_latest_status_ids(key, value):
    # TODO: change the file storage to database
    file_name = "ids.txt"
    file_path = os.path.realpath('.') + '/content/' + file_name

    ids = load_latest_status_ids()

    ids[key] = value
    with open(file_path, 'w+') as file:
        for key, value in ids.items():
            file.write(key + ":" + str(value) + "\n")


# TODO: temp method
def get_app_root():
    try:
        return os.environ['INTEREST_ENGINE_PATH']
    except KeyError:
        sys.stderr.write("Application Root environmental variable not set\n")
        sys.exit(1)


if __name__ == "__main__":
    # doc1 = 'It is only two months since Henrikh Mkhitaryan was the man in the same position Anthony Martial ' \
    #        'currently finds himself in. Held accountable for a poor workrate in the derby defeat to Manchester City ' \
    #        'in September, Mkhitaryan had to take the long road back into Jose Mourinho’s plans. Mkhitaryan is ' \
    #        'a great player. Martial must learn from Mkhitaryan. Hail Henrikh Mkhitaryan. Come one Henrikh!!! ' \
    #        'European Organization for Nuclear Research is a great place to be. Anthony Martial has been to the ' \
    #        'Nuclear Research center.'
    # tags = get_named_entity_tags(doc1)
    #
    # for tag in tags:
    #     print(tag.topic)
    #     print(str(tag.context))
    update_latest_status_ids('id', 'value')
