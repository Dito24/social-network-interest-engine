import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from feed_facebook.utils import get_post_score


# unit tests for generating post scores
def test_post_score_one():
    reactions = {'like': 10, 'love': 5, 'wow': 2}
    shares = 6

    expected_output = 1.695

    assert round(get_post_score(reactions, shares), 3) == expected_output


def test_post_score_two():
    reactions = {'like': 100, 'love': 50, 'wow': 9}
    shares = 23

    expected_output = 3.312

    assert round(get_post_score(reactions, shares), 3) == expected_output


def test_zero_reactions_zero_shares():
    reactions = {'like': 0, 'love': 0, 'wow': 0}
    shares = 0

    expected_output = 0

    assert get_post_score(reactions, shares) == expected_output


def test_no_reactions_no_shares():
    reactions = None
    shares = None

    expected_output = None

    assert get_post_score(reactions, shares) == expected_output


def test_only_likes():
    reactions = {'like': 0, 'love': None}
    shares = 12

    expected_output = 2.113

    assert round(get_post_score(reactions, shares), 3) == expected_output


def test_negative_shares():
    favorites = {'like': 100, 'love': 50, 'wow': 9}
    shares = -10

    expected_output = None

    assert get_post_score(favorites, shares) == expected_output


def test_negative_favorites():
    favorites = {'like': -100, 'love': 50, 'wow': 9}
    shares = 10

    expected_output = 2.450

    assert round(get_post_score(favorites, shares), 3) == expected_output
