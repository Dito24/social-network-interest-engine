import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.concepts import SocialNetworkFeed
from social_networks.utils import load_latest_status_ids, update_latest_status_ids
from feed_twitter.client import TwitterClient
from feed_twitter.utils import convert_tweets_to_native_statuses, get_twitter_trends


class TwitterFeedMapper(SocialNetworkFeed):
    def __init__(self, username, access_token, access_secret):
        self.client = TwitterClient(username=username, user_access_token=access_token, user_access_secret=access_secret)

    def get_public_trends_feed(self, **coordinates):
        # get world trends
        global_woe_id = 1
        world_trends = get_twitter_trends(self.client, global_woe_id)

        if ('latitude' in coordinates) & ('longitude' in coordinates):
            # get local trends
            response_data = self.client.client.trends_closest(coordinates['latitude'], coordinates['longitude'])
            locality_woe_id = response_data[0]['woeid']
            local_trends = get_twitter_trends(self.client, locality_woe_id)

            merged_trends = list(set(world_trends) | set(local_trends))

            return merged_trends
        else:
            return world_trends

    def get_user_timeline_feed(self):
        # capture the optional id value of the tweet since which tweets are to be returned
        last_id = None
        ids = load_latest_status_ids()
        if 'twitter_user_timeline' in ids:
            last_id = ids['twitter_user_timeline']

        # load tweets from user timeline
        if last_id is None:
            tweets = self.client.client.user_timeline(screen_name=self.client.username, count=30)
        else:
            tweets = self.client.client.user_timeline(screen_name=self.client.username, since_id=last_id)

        # convert tweets to application specific status objects
        statuses = convert_tweets_to_native_statuses(tweets)

        if len(statuses) > 0:
            update_latest_status_ids('twitter_user_timeline', statuses[0].id)

        return statuses

    def get_bookmarks_feed(self):
        # capture the optional id value of the tweet since which tweets are to be returned
        last_id = None
        ids = load_latest_status_ids()
        if 'twitter_bookmarks' in ids:
            last_id = ids['twitter_bookmarks']

        # load tweets from favorites
        if last_id is None:
            tweets = self.client.client.favorites(screen_name=self.client.username, count=30)
        else:
            tweets = self.client.client.favorites(screen_name=self.client.username, since_id=last_id)

        # convert tweets to application specific status objects
        statuses = convert_tweets_to_native_statuses(tweets)

        if len(statuses) > 0:
            update_latest_status_ids('twitter_bookmarks', statuses[0].id)

        return statuses

    def get_followings_feed(self):
        tweets = self.client.client.home_timeline(screen_name=self.client.username, count=10)

        # convert tweets to application specific status objects
        statuses = convert_tweets_to_native_statuses(tweets)

        return statuses

    def get_community_feed(self):
        pass

if __name__ == '__main__':
    obj = TwitterFeedMapper(access_token=os.environ['TWITTER_ACCESS_TOKEN'],
                            access_secret=os.environ['TWITTER_ACCESS_SECRET'], username=os.environ['TWITTER_USERNAME'])

    # for post in obj.get_followings_feed():
    #     print(post.text)
    #     print(post.score)
    #     print()

    lat = 7.2905720
    long = 80.6337260
    for trend in obj.get_public_trends_feed(latitude=lat, longitude=long):
        print(trend)

    # for status in obj.get_user_timeline_feed():
    #     print(status.text)
    #     print(status.score)
    #     print()
