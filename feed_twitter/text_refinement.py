# -*- coding: utf-8 -*-
import os
import re
import sys

from nltk.tokenize import TweetTokenizer

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from text_analysis.text_refinement import is_english, refine_entities


def refine_tweet_text(text):
    if text is None:
        return None

    # removes re-tweet/via
    new_text = re.sub('[\s]*RT[\s]*|[\s]*/via[\s]*', '', text)
    # new_text = re.sub('\s?RT.*:[\s]|\s?via.*:[\s]', '', text)

    # removes URLs
    new_text = re.sub(
        '(ftp|http[s]?)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', new_text)

    # refine entities
    hashtag_pattern = re.compile('(#\w+)')
    username_pattern = re.compile('(@\w+)')

    for word in hashtag_pattern.findall(new_text):
        sub = refine_entities(word)
        if sub is not None:
            new_text = re.sub(word, sub, new_text)
        else:
            new_text = re.sub(word, '', new_text)

    for word in username_pattern.findall(new_text):
        sub = refine_entities(word)
        if sub is not None:
            new_text = re.sub(word, sub, new_text)
        else:
            new_text = re.sub(word, '', new_text)

    # remove starting and trailing whitespaces
    new_text = new_text.lstrip().rstrip()

    # tokenize the string and filter out non-English language usage
    tokenizer = TweetTokenizer()
    tokens = tokenizer.tokenize(new_text)
    new_text = " ".join([token for token in tokens if is_english(token)])

    return new_text
