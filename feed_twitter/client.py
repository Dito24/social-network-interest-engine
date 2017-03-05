import os
import sys
from tweepy import API
from tweepy import OAuthHandler


class TwitterClient:
    def __init__(self, username=None, user_access_token=None, user_access_secret=None):
        self.client = self.get_twitter_client(user_access_token, user_access_secret)
        self.username = username

    def get_twitter_client(self, user_access_token, user_access_secret):
        authentication = self.get_twitter_auth(user_access_token, user_access_secret)

        if authentication is None:
            return None

        client = API(authentication)
        return client

    @staticmethod
    def get_twitter_auth(user_access_token, user_access_secret):
        if not user_access_secret or not user_access_token:
            return None

        try:
            consumer_key = os.environ['TWITTER_CONSUMER_KEY']
            consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        except KeyError:
            sys.stderr.write("TWITTER_* environment variables not set\n")
            sys.exit(1)

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(user_access_token, user_access_secret)
        return auth


if __name__ == "__main__":
    try:
        client_username = os.environ['TWITTER_USERNAME']
        access_token = os.environ['TWITTER_ACCESS_TOKEN']
        access_secret = os.environ['TWITTER_ACCESS_SECRET']
    except KeyError:
        sys.exit(1)

    # potential test cases

    # 1. successful creation of the object
    client_one = TwitterClient(client_username, access_token, access_secret)
    print(client_one.client)
    print(client_one.username)

    # 2. no access access_token passed
    client_two = TwitterClient(username=client_username, user_access_secret=access_secret)
    print(client_two.client)
    print(client_two.username)

    # 3. no access secret passed
    client_three = TwitterClient(username=client_username, user_access_token=access_token)
    print(client_three.client)
    print(client_three.username)
