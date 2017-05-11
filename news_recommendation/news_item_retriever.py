import feedparser
from urllib.parse import urlencode


def get_news_items(entities):
    if entities is None:
        return

    if not entities:
        return

    parameters = {'q': entities, 'output': 'rss'}
    feed = feedparser.parse('https://news.google.com/news?' + urlencode(parameters))
    items = feed['entries']

    news_items = {}
    for item in items:
        news_items[item['title']] = item['link']

    return news_items


if __name__ == '__main__':
    # get_news_items(['Paul Pogba', 'Manchester United'])
    print(get_news_items(['Mahinda Rajapakse', 'Sri Lanka']))
    get_news_items([])
