from interests import compute_community_interests
from news_item_retriever import get_news_items


def get_community_interest_news_items():
    community_interests = compute_community_interests()

    community_interest_news_items = {}
    for interest in community_interests:
        topic = interest[0].topic
        items = get_news_items([topic])
        community_interest_news_items[interest[0]] = items

    return community_interest_news_items


if __name__ == '__main__':
    print('Community interest suggestions:')
    for news_interest, news in get_community_interest_news_items().items():
        print(news_interest.topic)
        print(news[0].link)
