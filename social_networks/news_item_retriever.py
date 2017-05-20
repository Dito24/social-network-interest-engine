import feedparser
from urllib.parse import urlencode


class NewsItem:
    def __init__(self, topic, link):
        self.topic = topic
        self.link = link

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.link == other.link:
                return True
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


def get_news_items(entities):
    if entities is None:
        return

    if not entities:
        return

    entities = list(set(entities))

    parameters = {'q': entities, 'output': 'rss'}
    feed = feedparser.parse('https://news.google.com/news?' + urlencode(parameters))
    items = feed['entries']

    news_items = []
    for item in items:
        news_items.append(NewsItem(item['title'], item['link']))

    return news_items
