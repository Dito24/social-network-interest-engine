import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from feed_facebook.text_refinement import refine_facebook_post


def test_removal_of_https():
    test_case = '@ChirangaAlwis has a LinkedIn profile and it can be found at https://www.linkedin.com/'
    expected_output = 'Chiranga Alwis has a LinkedIn profile and it can be found at'

    assert refine_facebook_post(test_case) == expected_output


def test_removal_of_http():
    test_case = '@ChirangaAlwis has a LinkedIn profile and it can be found at http://www.linkedin.com/'
    expected_output = 'Chiranga Alwis has a LinkedIn profile and it can be found at'

    assert refine_facebook_post(test_case) == expected_output


def test_removal_of_ftp():
    test_case = '@ChirangaAlwis has a ftp resource and it can be found at ' \
                'ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    expected_output = 'Chiranga Alwis has a ftp resource and it can be found at'

    assert refine_facebook_post(test_case) == expected_output


def test_refining_username_one():
    test_case = '@barackObama has a ftp resource and it can be found at ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    expected_output = 'barack Obama has a ftp resource and it can be found at'

    assert refine_facebook_post(test_case) == expected_output


def test_refining_username_two():
    test_case = '@BarackObama has a ftp resource and it can be found at ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    expected_output = 'Barack Obama has a ftp resource and it can be found at'

    assert refine_facebook_post(test_case) == expected_output


# TODO: Introduce a dictionary for cases like AUSvsNZ and etc.
def test_refining_username_three():
    test_case = '@barackobama has a ftp resource and it can be found at ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    expected_output = 'barack obama has a ftp resource and it can be found at'

    assert refine_facebook_post(test_case) != expected_output


# TODO: Introduce a dictionary for cases like AUSvsNZ and etc.
def test_refining_username_four():
    test_case = '@Barackobama has a ftp resource and it can be found at ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    expected_output = 'Barack obama has a ftp resource and it can be found at'

    assert refine_facebook_post(test_case) != expected_output


def test_refining_hashtag_one():
    test_case = '#ThisIsAHashtag123 has a ftp resource and it can be found at ' \
             'ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    expected_output = 'This Is A Hashtag 123 has a ftp resource and it can be found at'

    assert refine_facebook_post(test_case) == expected_output


# TODO: Introduce a dictionary for cases like AUSvsNZ and etc.
def test_refining_hashtag_two():
    test_case = 'What a game it was #AUSvsNZ, loved it क्रिकेट के गौरवशाली खेल.'
    expected_output = 'What a game it was AUS vs NZ loved it .'

    assert refine_facebook_post(test_case) != expected_output


def test_refining_no_text():
    test_case = ''
    expected_output = None

    assert refine_facebook_post(test_case) != expected_output
