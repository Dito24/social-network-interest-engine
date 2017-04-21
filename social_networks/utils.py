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
from social_networks.concepts import SocialNetworkStatus, Tag
from social_networks.linked_data import get_ontology_data
from text_analysis.text_analytics import extract_entities


# Store social network statuses
def store_statuses(statuses, file_path):
    with open(file_path, 'a+') as file:
        for status in statuses:
            if status.text:
                file.write(json.dumps(get_status_text(status), default=jdefault) + "\n")


def get_status_text(status):
    tags = []
    if status.text:
        # TODO: testing purposes
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

    # TODO: for testing
    print(str(entities))
    # entities = get_entity_fractions(entities, text)

    tags = []
    for entity in entities:
        data = get_ontology_data(entity)

        if not data:
            data = get_ontology_data(entity)

        for datum in data:
            context = {'details': datum['details'], 'description': datum['description'], 'sub_types': datum['types']}

            tag = Tag(datum['name'], context, original=entity)
            if tag not in tags:
                tags.append(tag)

    return tags


# load status instances
def load_status(status_text):
    if status_text is None:
        return None

    status_dict = json.loads(status_text)
    created_at = get_datetime(status_dict['Created_At'])
    status_dict['Created_At'] = created_at
    status_dict['Score'] = decay_base_score(status_dict['Score'], created_at)
    tag_dict = status_dict['Tags']

    tag_list = []
    for tag_text in tag_dict:
        tag_list.append(
            Tag(topic=tag_text['topic'], original=tag_text['original'], context=tag_text['context']))

    return SocialNetworkStatus(native_identifier=status_dict['Id'], created=status_dict['Created_At'],
                               score=status_dict['Score'], text=tag_list)


def load_statuses_by_date(file_path):
    status_instances = {}

    with open(file_path, 'r') as file:
        for line in file:
            status_instance = load_status(line)
            if status_instance.created.year in status_instances:
                if status_instance.created.month not in status_instances[status_instance.created.year]:
                    status_instances[status_instance.created.year][status_instance.created.month] = []
                (status_instances[status_instance.created.year][status_instance.created.month]).append(status_instance)
            else:
                status_instances[status_instance.created.year] = {}
                status_instances[status_instance.created.year][status_instance.created.month] = []
                (status_instances[status_instance.created.year][status_instance.created.month]).append(status_instance)

    return status_instances


def load_statuses(file_path):
    status_instances = []

    with open(file_path, 'r') as file:
        for line in file:
            status_instances.append(load_status(line))

    return status_instances


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


def get_datetime(text):
    if text is None:
        return None

    datetime_instance = validate_datetime(text, "%Y-%m-%d %H:%M:%S")
    if datetime_instance is None: datetime_instance = validate_datetime(text, "%Y-%m-%dT%H:%M:%S+0000")

    return datetime_instance


def validate_datetime(text, expected_format):
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
