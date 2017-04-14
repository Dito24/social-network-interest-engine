import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.linked_data import get_tag_domains
# from social_networks.updater import load_bookmarks, load_followings, load_timeline, update_bookmarks, update_timeline
from social_networks.utils import build_interest_topic_tree, get_app_root, load_statuses


def compute_interests():
    # bookmarks = load_bookmarks()
    # followings = load_followings()
    # timeline = load_timeline()
    #
    # update_bookmarks(bookmarks)
    # update_timeline(timeline)

    bookmarks = load_statuses(get_app_root() + '/content/bookmarks.jsonl')
    timeline = load_statuses(get_app_root() + '/content/timeline.jsonl')
    statuses = bookmarks + timeline

    sorted_statuses = sorted(statuses, key=lambda status_instance: status_instance.score, reverse=True)

    universal_tag_collection = []

    for status in sorted_statuses:
        tags = set(status.text)
        if len(tags) > 0:
            for tag in tags:
                if tag.topic:
                    universal_tag_collection.append(tag)

    for status in sorted_statuses[:10]:
        tags = set(status.text)
        if len(tags) > 0:
            domains = get_tag_domains(tags)

            for tag in tags:
                if tag.topic:
                    print(tag.topic + ' ' + str(tag.context['sub_types']))
                    universal_tag_collection.append(tag)

            if domains:
                print(list(set(domains)))

            print(status.score)
            print()

    tree = build_interest_topic_tree(universal_tag_collection)
    tree.show()


if __name__ == '__main__':
    compute_interests()
