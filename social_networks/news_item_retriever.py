import feedparser
# import os
# import sys
from urllib.parse import urlencode

# try:
#     sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
# except KeyError:
#     sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
#     sys.exit(1)
# print(sys.path)
from interests import compute_current_interest_contexts


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


def get_current_interest_news_items():
    contexts = compute_current_interest_contexts()

    current_interest_news_items = {}
    for context in contexts:
        topics = []
        for tag in context[0].text:
            topics.append(tag.topic)

        items = get_news_items(topics)
        current_interest_news_items[str(topics)] = items

    return current_interest_news_items


if __name__ == '__main__':
    for interests, news in get_current_interest_news_items().items():
        print(interests)

        if news:
            print(news[0].link)

        # for link in news:
        #     print(link.link)

        print()
