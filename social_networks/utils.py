from datetime import datetime
import json
import math
import os
import re
import sys
from treelib import Node, Tree

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.concepts import Tag
from social_networks.linked_data import get_ontology_data, get_ontology_super_class
from text_analysis.text_analytics import extract_entities, get_entity_fractions


# store social network statuses
def store_statuses(statuses, file_path):
    with open(file_path, 'a+') as file:
        for status in statuses:
            if status.text:
                file.write(json.dumps(get_status_text(status), default=jdefault) + "\n")


def get_status_text(status):
    tags = []
    if status.text:
        print(status.text)

        tags = get_named_entity_tags(status.text)

    status_record = {'Id': status.id, 'Created_At': status.created, 'Score': status.score, 'Tags': tags}

    return status_record


def jdefault(o):
    return o.__dict__


def get_named_entity_tags(text):
    entities = extract_entities(text)
    entities = get_entity_fractions(entities, text)

    tags = []
    for entity in entities:
        data = get_ontology_data(entity['entity'])

        if not data:
            data = get_ontology_data(entity['entity'])

        for datum in data:
            # TODO: Attempt to use standard Python API to get everything including the types
            context = {'type': datum[1], 'description': datum[2], 'sub_types': datum[4]}

            # context = {'type': datum[1], 'description': datum[2]}

            tag = Tag(datum[0], context, context_fraction=entity['fraction'])
            if tag not in tags:
                tags.append(tag)

    return tags


# load status instances
def load_statuses(file_path):
    statuses = {}

    with open(file_path, 'r') as file:
        for line in file:
            status = json.loads(line)

            created_at = datetime.strptime(status['Created_At'], "%Y-%m-%d %H:%M:%S")
            status['Created_At'] = created_at
            status['Score'] = decay_base_score(status['Score'], created_at)

            if status['Created_At'].year in statuses:

                if not status['Created_At'].month in statuses[status['Created_At'].year]:
                    statuses[status['Created_At'].year][status['Created_At'].month] = []

                (statuses[status['Created_At'].year][status['Created_At'].month]).append(status)

            else:

                statuses[status['Created_At'].year] = {}

                statuses[status['Created_At'].year][status['Created_At'].month] = []

                (statuses[status['Created_At'].year][status['Created_At'].month]).append(status)

    return statuses


def decay_base_score(base_score, created_at):
    time_difference = (datetime.now() - created_at)
    time_difference_in_days = (time_difference.days * 86400 + time_difference.seconds) / 86400

    # start decaying the score after two days
    drop_off = 2
    if time_difference_in_days > drop_off:
        decayed_score = base_score * math.exp(
            -5 * (time_difference_in_days - drop_off) * (time_difference_in_days - drop_off))
    else:
        decayed_score = base_score

    return decayed_score


# load the latest, stored status ids from supported social networks
def load_latest_status_ids():
    # TODO: change the file storage to database
    file_name = "ids.txt"
    file_path = get_app_root() + '/content/' + file_name

    ids = dict()

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if ":" in line:
                    content = re.split('[:]', line)
                    ids[content[0]] = content[1].strip('\n')

    return ids


# update the stored status ids with latest ids from supported social networks
def update_latest_status_ids(key, value):
    # TODO: change the file storage to database
    file_name = "ids.txt"
    file_path = get_app_root() + '/content/' + file_name

    ids = load_latest_status_ids()

    ids[key] = value
    with open(file_path, 'w+') as file:
        for key, value in ids.items():
            file.write(key + ":" + str(value) + "\n")


def build_interest_topic_tree(tags):
    if not tags:
        return None

    clusters = Tree()

    for tag in tags:
        try:
            sub_types = tag.context['sub_types']
        except (KeyError, TypeError):
            continue

        if sub_types is not None:
            sorted_types = sort_class_order(sub_types)
            if sorted_types is not None:
                sorted_types.insert(0, 'Thing')
                create_branch(clusters, sorted_types)

    return clusters


def create_branch(tree_structure, types):
    if not (tree_structure, types):
        return

    previous = None
    for class_type in types:
        node = Node(identifier=class_type, data=[])

        if previous is None:
            if tree_structure.get_node(node.identifier) is None:
                tree_structure.add_node(node)
        else:
            if tree_structure.get_node(node.identifier) is None:
                tree_structure.add_node(node, previous.identifier)

        previous = node


def sort_class_order(types):
    if not types:
        return None

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


# TODO: temp method
def get_app_root():
    try:
        return os.environ['INTEREST_ENGINE_PATH']
    except KeyError:
        sys.stderr.write("Application Root environmental variable not set\n")
        sys.exit(1)

if __name__ == "__main__":
    statuses = load_statuses(get_app_root() + '/content/bookmarks.jsonl')

    tags = []

    for year, months in statuses.items():

        print('Year: ' + str(year))

        for month, statuses in months.items():

            print('Month: ' + str(month))

            for status in statuses:
                if len(status['Tags']) == 0:
                    continue

                tags.extend(status['Tags'])

                print('Status score: ' + str(status['Score']))
                for tag in status['Tags']:
                    print('Entity: ' + tag['topic'])
                    print('Score: ' + str(tag['importance'] * status['Score']))
                    print('Type: ' + tag['context']['type'])
                    print('Description: ' + tag['context']['description'])
                    print()
                print()

            print()

        print()

    new = []
    for tag in tags:
        new.append(Tag(topic=tag['topic'], context_fraction=tag['importance'], context=tag['context']))

    print(new)
    build_interest_topic_tree(new).show()


#     load_latest_status_ids()
#     doc1 = 'It is only two months since Henrikh Mkhitaryan was the man in the same position Anthony Martial ' \
#            'currently finds himself in. Held accountable for a poor workrate in the derby defeat to Manchester City ' \
#            'in September, Mkhitaryan had to take the long road back into Jose Mourinho’s plans. Mkhitaryan is ' \
#            'a great player. Martial must learn from Mkhitaryan. Hail Henrikh Mkhitaryan. Come one Henrikh!!! ' \
#            'European Organization for Nuclear Research is a great place to be. Anthony Martial has been to the ' \
#            'Nuclear Research center.'
#     tags = get_named_entity_tags(doc1)
#
#     for tag in tags:
#         print(tag.topic)
#         print(str(tag.context))
#     update_latest_status_ids('id', 'value')
