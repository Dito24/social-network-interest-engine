import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from text_analysis.text_refinement import break_blocks, refine_entities


# unit tests for breaking words
def test_breaking_end_digit_block():
    test_case = 'TestCase123'
    expected_output = 'Test Case 123'

    assert break_blocks(test_case) == expected_output


def test_breaking_front_digit_block():
    test_case = '04thOfJuly'
    expected_output = '04 th Of July'

    assert break_blocks(test_case) == expected_output


def test_breaking_middle_digit_block():
    test_case = 'Test123Case'
    expected_output = 'Test 123 Case'

    assert break_blocks(test_case) == expected_output


def test_breaking_singular_digit_block():
    test_case = 'No1DonaldTrumpNo2Hillary Clinton'
    expected_output = 'No 1 Donald Trump No 2 Hillary Clinton'

    assert break_blocks(test_case) == expected_output


def test_breaking_end_capital_letter_block():
    test_case = 'ThisMustBeEASY'
    expected_output = 'This Must Be EASY'

    assert break_blocks(test_case) == expected_output


def test_breaking_front_capital_letter_block():
    test_case = 'THISMustBeEasy'
    expected_output = 'THIS Must Be Easy'

    assert break_blocks(test_case) == expected_output


def test_breaking_middle_capital_letter_block():
    test_case = 'ThisMUSTBeEasy'
    expected_output = 'This MUST Be Easy'

    assert break_blocks(test_case) == expected_output


# TODO: Introduce a dictionary for cases like AUSvsNZ and etc.
def test_breaking_random_capital_letter_blocks_one():
    test_case = 'AUSvsNZ'
    expected_output = 'AUS vs NZ'

    assert break_blocks(test_case) != expected_output


def test_breaking_random_capital_letter_blocks_two():
    test_case = 'ThisMUSTBeEXTREMELYEasyFORYou'
    expected_output = 'This MUST Be EXTREMELY Easy FOR You'

    assert break_blocks(test_case) == expected_output


# TODO: Introduce a dictionary for cases like AUSvsNZ and etc.
def test_breaking_complete_uppercase_words():
    test_case = 'DONALDTRUMP'
    expected_output = 'DONALD TRUMP'

    assert break_blocks(test_case) != expected_output


def test_breaking_complete_lowercase_words():
    test_case = 'donaldtrump'
    expected_output = 'donaldtrump'

    assert break_blocks(test_case) == expected_output


def test_breaking_end_underscore():
    test_case = 'donald_trump_'
    expected_output = 'donald trump'

    assert break_blocks(test_case) == expected_output


def test_breaking_front_underscore():
    test_case = '_donald_JohnTrump'
    expected_output = 'donald John Trump'

    assert break_blocks(test_case) == expected_output


def test_breaking_middle_underscore():
    test_case = 'donald_trump'
    expected_output = 'donald trump'

    assert break_blocks(test_case) == expected_output


# module level integrated tests
def test_non_english_language_detection_one():
    test_case = 'こんにちはJapanWelcomeTo日本'
    expected_output = 'Japan Welcome To'

    assert refine_entities(test_case) == expected_output


def test_non_english_language_detection_two():
    test_case = '12345こんにちはJapanWelcomeTo日本'
    expected_output = '12345 Japan Welcome To'

    assert refine_entities(test_case) == expected_output


def test_hashtag_sample_one():
    test_case = '#12345こんにちはJapanWelcomeTo日本'
    expected_output = '12345 Japan Welcome To'

    assert refine_entities(test_case) == expected_output


def test_hashtag_sample_two():
    test_case = '#BonjourTomCruise'
    expected_output = 'Bonjour Tom Cruise'

    assert refine_entities(test_case) == expected_output


def test_hashtag_sample_three():
    test_case = '#12345_icloud'
    expected_output = '12345 icloud'

    assert refine_entities(test_case) == expected_output


def test_username_filter():
    test_case = '@12345_icloudPrivacyLeak'
    expected_output = '12345 icloud Privacy Leak'

    assert refine_entities(test_case) == expected_output
