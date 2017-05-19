import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from feed_facebook.facebook_feed_mapper import FacebookFeedMapper
from feed_twitter.twitter_feed_mapper import TwitterFeedMapper
from social_networks.concepts import SocialNetworkFeed
from social_networks.utils import get_app_root, store_statuses

BOOKMARKS = get_app_root() + '/content/bookmarks.jsonl'
TIMELINE = get_app_root() + '/content/timeline.jsonl'

# TODO: some mechanism to get the tokens
SOCIAL_NETWORK_FEED = [
    FacebookFeedMapper(os.environ.get('FACEBOOK_ACCESS_TOKEN')),
    TwitterFeedMapper(access_token=os.environ['TWITTER_ACCESS_TOKEN'],
                      access_secret=os.environ['TWITTER_ACCESS_SECRET'], username=os.environ['TWITTER_USERNAME'])
]


def load_timeline():
    statuses = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            feed = feed.get_user_timeline_feed()
            if feed is not None:
                statuses.extend(feed)

    return statuses


def load_bookmarks():
    statuses = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            feed = feed.get_bookmarks_feed()
            if feed is not None:
                statuses.extend(feed)

    return statuses


def load_followings():
    statuses = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            feed = feed.get_followings_feed()
            if feed is not None:
                statuses.extend(feed)

    return statuses


def load_community_feed():
    members = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            feed = feed.get_community_feed()
            if feed is not None:
                members.extend(feed)

    return members


def load_trends():
    trend_topics = []

    for feed in SOCIAL_NETWORK_FEED:
        if isinstance(feed, SocialNetworkFeed):
            feed = feed.get_public_trends_feed()
            if feed is not None:
                trend_topics.extend(feed)

    return trend_topics


def update_timeline(statuses):
    if statuses:
        store_statuses(statuses, TIMELINE)


def update_bookmarks(statuses):
    if statuses:
        store_statuses(statuses, BOOKMARKS)


# if __name__ == "__main__":
#     for item in load_trends():
#         if item:
#             print(item)
