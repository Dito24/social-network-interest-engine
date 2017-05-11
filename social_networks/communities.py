import os
import sys

from social_networks.updater import load_community_feed

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.linked_data import sort_class_order
from social_networks.utils import build_interest_topic_tree, get_entity_tags, load_statuses, get_app_root


def cluster_community_members(members):
    if not members:
        return None

    # Concatenate member content prior to entity extraction
    content = []
    for member in members:
        content.append(member.content)
    content = [user_content for user_content in content if user_content is not None]
    content = ' '.join(content)
    print(content)

    # Extract named entities
    tags = get_entity_tags(content)
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
        sub_type = sort_class_order(sub_type)

        if sub_type is None:
            continue

        if len(sub_type) > 0:
            tree.get_node(sub_type[len(sub_type) - 1]).data.append(member)


def get_matching_clusters():
    members = load_community_feed()
    community_interest_tree = cluster_community_members(members)
    community_interest_tree.show()

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


if __name__ == '__main__':
    for topic, members in get_matching_clusters().items():
        print(topic)
        print(members)
        print()
