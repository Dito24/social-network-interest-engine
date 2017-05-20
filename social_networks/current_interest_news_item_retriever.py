from interests import compute_current_interest_contexts
from news_item_retriever import get_news_items


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
    print('Current interests:')
    for interests, news in get_current_interest_news_items().items():
        print(interests)

        if news:
            print(news[0].link)

        print()
