from interests import compute_trending_topics
from news_item_retriever import get_news_items


def get_trending_news_items():
    trends = compute_trending_topics()

    trending_news_items = {}
    for trend in trends:
        trending_topic = trend.topic
        items = get_news_items([trending_topic])
        trending_news_items[trending_topic] = items

    return trending_news_items

if __name__ == '__main__':
    print('Trending news items: ')
    for topic, news in get_trending_news_items().items():
        print(topic)
        print(news[0].link)
