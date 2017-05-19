import json

import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.linked_data import sort_class_order
from social_networks.utils import build_interest_topic_tree, get_entity_tags, load_statuses, get_app_root

from social_networks.concepts import SocialNetworkMember, Tag
TAGS = get_app_root() + '/content/tags.jsonl'
MEMBERS = get_app_root() + '/content/members.jsonl'


def cluster_community_members(members):
    # TODO: actual code

    # if not members:
    #     return None

    # Concatenate member content prior to entity extraction

    # content = []
    # for member in members:
    #     content.append(member.content)
    # content = [user_content for user_content in content if user_content is not None]
    # content = ' '.join(content)

    # Extract named entities
    # tags = get_entity_tags(content)

    # TODO: actual code

    # TODO:temporary demonstration code
    # store_members(members, MEMBERS)
    members = load_members(MEMBERS)

    content = []
    for member in members:
        content.append(member.content)
    content = [user_content for user_content in content if user_content is not None]
    content = ' '.join(content)

    # Extract named entities
    # tags = get_entity_tags(content)

    # TODO: temporary demonstration code
    # store_tags(tags, TAGS)
    tags = load_tags(TAGS)

    # Build community interest tree
    interest_tree = build_interest_topic_tree(tags)

    entities = {}
    for tag in tags:
        entities[tag] = tag.original

    for member in members:
        content = member.content

        identified_entities = []
        for key, value in entities.items():
            if content is not None:
                if value in content:
                    identified_entities.append(key)

        member.content = set(identified_entities)
        place_member(member, interest_tree)

    return interest_tree


def place_member(member, tree):
    if member is None or tree is None:
        return

    member_content = member.content

    sub_types = []
    for tag in member_content:
        sub_types.append(tag.context['sub_types'])

    for sub_type in sub_types:
        # TODO: review but already sorted
        # sub_type = sort_class_order(sub_type)

        if sub_type is None:
            continue

        if len(sub_type) > 0:
            tree.get_node(sub_type[len(sub_type) - 1]).data.append(member)


def get_matching_clusters():
    # TODO: temporary
    # members = load_community_feed()
    members = None
    community_interest_tree = cluster_community_members(members)

    # update_statuses()

    timeline = load_statuses(get_app_root() + '/content/timeline.jsonl')
    # followings = load_followings()
    bookmarks = load_statuses(get_app_root() + '/content/bookmarks.jsonl')

    # statuses = bookmarks + followings + timeline
    statuses = bookmarks + timeline
    sorted_statuses = sorted(statuses, key=lambda status_instance: status_instance.created, reverse=True)

    universal_tag_collection = []
    for status in sorted_statuses[:300]:
        universal_tag_collection.extend(status.text)

    types = []
    for tag in universal_tag_collection:
        sub_types = tag.context['sub_types']
        if len(sub_types) > 0:
            types.append(sub_types[len(sub_types) - 1])

    clustered_members = {}
    for sub_type in set(types):
        node = community_interest_tree.get_node(sub_type)

        if node is not None:
            if sub_type in clustered_members:
                clustered_members[sub_type].extend(node.data)
            else:
                clustered_members[sub_type] = []
                clustered_members[sub_type].extend(node.data)

    return {title: users for title, users in clustered_members.items() if len(users) > 0}


# temporary demonstration code
def store_members(members, file_path):
    with open(file_path, 'a+') as file:
        for member in members:
            if member.id:
                file.write(json.dumps(get_member_text(member), default=jdefault) + "\n")


def get_member_text(member):
    member_record = {'Id': member.id, 'Content': member.content}
    return member_record


def load_members(file_path):
    member_instances = []

    with open(file_path, 'r') as file:
        for line in file:
            member_instances.append(load_member(line))

    return member_instances


def load_member(member_text):
    if member_text is None:
        return None

    member_dict = json.loads(member_text)
    return SocialNetworkMember(identifier=member_dict['Id'], content=member_dict['Content'])


def store_tags(tags, file_path):
    with open(file_path, 'a+') as file:
        for tag in tags:
            if tag.topic:
                file.write(json.dumps(get_tag_text(tag), default=jdefault) + "\n")


def get_tag_text(tag):
    tag_record = {'Topic': tag.topic, 'Context': tag.context, 'Original': tag.original}
    return tag_record


def load_tags(file_path):
    tag_instances = []

    with open(file_path, 'r') as file:
        for line in file:
            tag_instances.append(load_tag(line))

    return tag_instances


def load_tag(tag_text):
    if tag_text is None:
        return None

    tag_dict = json.loads(tag_text)
    return Tag(topic=tag_dict['Topic'], context=tag_dict['Context'], original=tag_dict['Original'])


def jdefault(o):
    return o.__dict__

# if __name__ == '__main__':
#     for topic, members in get_matching_clusters().items():
#         print(topic)
#         print(members)
#         print()
