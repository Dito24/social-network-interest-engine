import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.linked_data import sort_class_order
from social_networks.utils import build_interest_topic_tree, get_entity_tags


def cluster_community_members(members):
    if not members:
        return None

    # Concatenate member content prior to entity extraction
    content = []
    for member in members:
        content.append(member.content)
    content = [user_content for user_content in content if user_content is not None]
    content = ' '.join(content)

    # Extract named entities
    tags = get_entity_tags(content)
    # Build community interest tree
    interest_tree = build_interest_topic_tree(tags)

    entities = {}
    for tag in tags:
        entities[tag] = tag.topic

    for member in members:
        content = member.content

        identified_entities = []
        for key, value in entities.items():
            if content is not None:
                if value in content:
                    identified_entities.append(key)

        member.content = set(identified_entities)
        place_member(member, interest_tree)

    print(interest_tree.paths_to_leaves())

    return interest_tree


def place_member(member, tree):
    if member is None or tree is None:
        return

    member_content = member.content

    sub_types = []
    for tag in member_content:
        sub_types.append(tag.context['sub_types'])

    for sub_type in sub_types:
        sub_type = sort_class_order(sub_type)

        if sub_type is None:
            continue

        if len(sub_type) > 0:
            tree.get_node(sub_type[len(sub_type) - 1]).data.append(member)
