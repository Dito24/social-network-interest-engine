import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from feed_facebook.text_refinement import refine_facebook_post


def test_one():
    test_1 = '@chira Emma Stone, La La Land.' \
             '' \
             '#Oscars' \
             'The Academy'

    assert refine_facebook_post(test_1) == 'chira Emma Stone , La La Land.Oscars The Academy'
