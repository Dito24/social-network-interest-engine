import math
import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from feed_twitter.text_refinement import refine_tweet_text
from social_networks.concepts import SocialNetworkMember, SocialNetworkStatus
from text_analysis.text_refinement import refine_entities


def convert_tweets_to_native_statuses(tweets):
    statuses = []

    for tweet in tweets:
        refined_text = refine_tweet_text(tweet.text)

        if not refined_text:
            continue

        if hasattr(tweet, 'retweeted_status'):
            favorite_count = tweet.retweeted_status.favorite_count
        else:
            favorite_count = tweet.favorite_count

        statuses.append(SocialNetworkStatus(native_identifier=tweet.id,
                                            text=refined_text, created=str(tweet.created_at),
                                            score=generate_tweet_score(favorite_count, tweet.retweet_count)))

    return statuses


def generate_tweet_score(favorites, shares):
    if favorites is None or shares is None:
        return None

    if favorites < 0 or shares < 0:
        return None

    weigh_like = 1
    weigh_share = 10

    total = 0
    total += (favorites * weigh_like)
    total += (shares * weigh_share)

    base_score = total / (weigh_like + weigh_share)

    return math.log(max(base_score, 1))


def get_twitter_trends(twitter_client, woe_id):
    if not (twitter_client, woe_id):
        return None

    response_data = twitter_client.client.trends_place(woe_id)

    trends = []
    for content in (response_data[0]['trends']):
        trends.append(refine_entities(content['name']))

    return trends


def get_member_instance(member_identifier, content):
    if not member_identifier:
        return None

    return SocialNetworkMember(identifier=member_identifier, content=content)


def get_statuses_text(username, tweets):
    if username is None or tweets is None:
        return None

    content = []
    for tweet in tweets:
        content.append(refine_tweet_text(tweet.text))

    return " ".join(content)
