import json
import math
import os
import re
import sys
from datetime import datetime

from treelib import Node, Tree

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.concepts import Tag
from social_networks.linked_data import get_ontology_data
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

        tags = get_entity_tags(status.text)

    status_record = {'Id': status.id, 'Created_At': status.created, 'Score': status.score, 'Tags': tags}

    return status_record


def jdefault(o):
    return o.__dict__


def get_entity_tags(text):
    if text is None:
        return None

    entities = extract_entities(text)
    entities = get_entity_fractions(entities, text)

    tags = []
    for entity in entities:
        data = get_ontology_data(entity['entity'])

        if not data:
            data = get_ontology_data(entity['entity'])

        for datum in data:
            context = {'details': datum['details'], 'description': datum['description'], 'sub_types': datum['types']}

            tag = Tag(datum['name'], context, context_fraction=entity['fraction'])
            if tag not in tags:
                tags.append(tag)

    return tags


# load status instances
def load_statuses(file_path):
    statuses = {}

    with open(file_path, 'r') as file:
        for line in file:
            status = json.loads(line)

            created_at = get_datetime(status['Created_At'], "%Y-%m-%d %H:%M:%S")
            if created_at is None:
                created_at = datetime.strptime(status['Created_At'], "%Y-%m-%dT%H:%M:%S+0000")

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


# build interest tree
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
            sub_types = [sub_type for sub_type in sub_types if sub_type is not None]
            sub_types.insert(0, 'Thing')
            # print(sub_types)
            create_branch(clusters, sub_types)

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


def add_interest_tags(tree_structure, tags):
    if not (tags, tree_structure):
        return None

    for tag in tags:
        try:
            sub_types = tag.context['sub_types']
        except (KeyError, TypeError):
            continue

        if sub_types is not None:
            sub_types = [sub_type for sub_type in sub_types if sub_type is not None]
            if sub_types:
                index = 0
                data = tree_structure.get_node(sub_types[len(sub_types) - 1]).data

                while index < len(data):
                    if data[index][0] == tag:
                        data[index] = (tag, data[index][1] + 1)
                        break

                    index += 1

                if index == len(data):
                    data.append((tag, 1))
                # tree_structure.get_node(sub_types[len(sub_types) - 1]).data.append(tag)


def get_datetime(text, expected_format):
    if text is None or expected_format is None:
        return None

    try:
        return datetime.strptime(text, expected_format)
    except ValueError:
        return None


# TODO: temp method
def get_app_root():
    try:
        return os.environ['INTEREST_ENGINE_PATH']
    except KeyError:
        sys.stderr.write("Application Root environmental variable not set\n")
        sys.exit(1)


if __name__ == "__main__":
    bookmarks = load_statuses(get_app_root() + '/content/bookmarks.jsonl')
    timeline = load_statuses(get_app_root() + '/content/timeline.jsonl')
    statuses = {**bookmarks, **timeline}

    tags = []

    for year, months in statuses.items():

        for month, statuses in months.items():

            for status in statuses:
                if len(status['Tags']) == 0:
                    continue

                tags.extend(status['Tags'])

    new = []
    for tag in tags:
        new.append(Tag(topic=tag['topic'], context_fraction=tag['importance'], context=tag['context']))

    tree = build_interest_topic_tree(new)

    add_interest_tags(tree, new)

    tree.show()

    for item in tree.get_node('Soccer Player').data:
        print(item[0].topic)
        print(item[0].context)
        print(item[1])
        print()

    # data_nodes = tree.all_nodes()
    #
    # sorted_list = sorted(data_nodes, key=lambda node: len(node.data))
    # sorted_list = reversed(sorted_list)
    # # filter empty data nodes
    # sorted_list = [node for node in sorted_list if node.data]
    #
    # top = sorted_list[:10]


# load_latest_status_ids()
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
