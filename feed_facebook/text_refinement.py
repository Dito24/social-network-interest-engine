# -*- coding: utf-8 -*-
import os
import re
import sys

from nltk.tokenize import word_tokenize

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from text_analysis.text_refinement import is_english, refine_entities


def refine_facebook_post(text):
    if text is None:
        return None

    # removes URLs
    new_text = re.sub('(ftp|http[s]?)://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

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
    tokens = word_tokenize(new_text)
    new_text = " ".join([token for token in tokens if is_english(token)])

    return new_text

if __name__ == '__main__':
    # test 1:chira Emma Stone, La La Land. Oscars The Academy
    test_1 = '@chira Emma Stone, La La Land.' \
           '' \
           '#Oscars' \
           'The Academy'

    print(refine_facebook_post(test_1))

    # test 2: remove the URL (HTTPS)
    test_2 = '@ChirangaAlwis has a LinkedIn profile and it can be found at https://www.linkedin.com/'
    print(refine_facebook_post(test_2))

    # test 3: remove the URL (HTTP)
    test_3 = '@ChirangaAlwis has a LinkedIn profile and it can be found at http://www.linkedin.com/'
    print(refine_facebook_post(test_3))

    # test 4: remove the URL (FTP)
    test_4 = '@ChirangaAlwis has a ftp resource and it can be found at ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    print(refine_facebook_post(test_4))

    # test 5: refine username/hashtag
    test_5 = '@barackObama has a ftp resource and it can be found at ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    print(refine_facebook_post(test_5))

    # test 6: refine username/hashtag failure
    test_6 = '@BarackObama has a ftp resource and it can be found at ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    print(refine_facebook_post(test_6))

    # test 7: refine username/hashtag failure
    test_7 = '@barackobama has a ftp resource and it can be found at ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    print(refine_facebook_post(test_7))

    # test 8: refine username/hashtag failure
    test_8 = '@Barackobama has a ftp resource and it can be found at ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    print(refine_facebook_post(test_8))

    # test 9: refine username/hashtag
    test_9 = '#ThisIsAHashtag123 has a ftp resource and it can be found at ' \
             'ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt '
    print(refine_facebook_post(test_9))

    # test 10: refine username/hashtag failure
    test_10 = 'What a game it was #AUSvsNZ, loved it'
    print(refine_facebook_post(test_10))

    # test 11: non English language words
    test_11 = 'What a game it was #AUSvsNZ, loved it. क्रिकेट के गौरवशाली खेल.'
    print(refine_facebook_post(test_11))
