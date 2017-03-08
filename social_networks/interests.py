import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.updater import load_bookmarks, load_followings, load_timeline, update_bookmarks, update_timeline


def compute_interests():
    bookmarks = load_bookmarks()
    # followings = load_followings()
    timeline = load_timeline()

    update_bookmarks(bookmarks)
    update_timeline(timeline)




if __name__ == '__main__':
    compute_interests()
