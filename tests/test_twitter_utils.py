import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from feed_twitter.utils import generate_tweet_score


# unit tests for generating tweet scores
def test_zero_favorites_zero_shares():
    favorites = 0
    shares = 0

    expected_output = 0

    assert generate_tweet_score(favorites, shares) == expected_output


def test_no_favorites_no_shares():
    favorites = None
    shares = None

    expected_output = None

    assert generate_tweet_score(favorites, shares) == expected_output


def test_only_no_shares():
    favorites = 0
    shares = None

    expected_output = None

    assert generate_tweet_score(favorites, shares) == expected_output


def test_tweet_score_one():
    favorites = 100
    shares = 50

    expected_output = 3.999

    assert round(generate_tweet_score(favorites, shares), 3) == expected_output


def test_tweet_score_two():
    favorites = 1000
    shares = 1

    expected_output = 4.520

    assert round(generate_tweet_score(favorites, shares), 3) == expected_output


def test_negative_args():
    favorites = -1
    shares = -10

    expected_output = None

    assert generate_tweet_score(favorites, shares) == expected_output


def test_negative_favorites():
    favorites = -1
    shares = 10

    expected_output = None

    assert generate_tweet_score(favorites, shares) == expected_output
