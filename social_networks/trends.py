from collections import OrderedDict
import os
from retrying import retry
import sys
from time import sleep

from pytrends.request import TrendReq
from json import JSONDecodeError
from pytrends.request import ResponseError, RateLimitError

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.concepts import SocialNetworkTrend, ZScore


def get_trend_data_client():
    # implementation refers to Google Trends' data
    try:
        google_username = os.environ['GOOGLE_USERNAME']
        google_password = os.environ['GOOGLE_SECRET']
    except KeyError:
        sys.stderr.write("GOOGLE_* environment variables not set\n")
        sys.exit(1)

    google_trends = TrendReq(google_username, google_password, custom_useragent=None)

    return google_trends

# create a client to acquire historical trend data
trend_data_client = get_trend_data_client()


@retry(wait_exponential_multiplier=1000, wait_exponential_max=20000, stop_max_delay=120000)
def get_historical_trends(keywords):
    payload = {'q': keywords, 'date': 'now 12-H'}

    try:
        response = trend_data_client.trend(payload, return_type='json')
    except (ResponseError, JSONDecodeError, RateLimitError):
        raise Exception("Retry!")

    results = OrderedDict()

    for row in response['table']['rows']:
        results.update({row['c'][0]['f']: row['c'][1]['v']})

    return results


def get_standard_score(keywords):
    historical_trends = []
    data = {}

    try:
        data = get_historical_trends(keywords)
    except Exception:
        print('arrived')

    if not data:
        return -1

    for date, value in data.items():
        historical_trends.append(value)

    historical_trends = list(reversed(historical_trends))

    historical_trends = [x for x in historical_trends if x is not None]

    current_trend = historical_trends[0]

    historical_trends = historical_trends[1:]

    z_score = ZScore(0.9, historical_trends)
    return z_score.get_score(current_trend)


def get_social_trend(index, queue, results):
    factor = int(index / 4)
    sleep(factor * 60)

    term = queue.get()
    z_score = get_standard_score(term)
    results.append(SocialNetworkTrend(topic=term, score=z_score))
    queue.task_done()


if __name__ == "__main__":
    print(str(get_standard_score('‪‪New York Knicks‬, ‪Madison Square Garden‬, ‪Golden State Warriors‬‬')))
