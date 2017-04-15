import operator
import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.linked_data import get_tag_domains
from social_networks.updater import load_bookmarks, load_followings, load_timeline, update_bookmarks, update_timeline, \
    load_community_feed
from social_networks.utils import get_app_root, load_statuses, load_statuses_by_date
from social_networks.communities import cluster_community_members


def compute_interests():
    # bookmarks = load_bookmarks()
    # followings = load_followings()
    # timeline = load_timeline()
    #
    # update_bookmarks(bookmarks)
    # update_timeline(timeline)

    bookmarks = load_statuses(get_app_root() + '/content/bookmarks.jsonl')
    timeline = load_statuses(get_app_root() + '/content/timeline.jsonl')

    # 0.5 weight for the timeline content
    for status in timeline:
        status.score = 0.5 * status.score

    # 0.25 weight for bookmarks content
    for status in bookmarks:
        status.score = 0.25 * status.score

    statuses = bookmarks + timeline

    final = []
    for status in statuses:
        if not status.text:
            continue

        # To avoid duplication of contexts (tag combinations)
        if status in final:
            index = final.index(status)
            final[index].score = final[index].score + status.score
        else:
            final.append(status)

    # Current interests
    # for item in compute_current_interests(final):
    #     print(item[0].score)

    # print(domain_frequency(statuses))

    monthly_timeline_statuses = load_statuses_by_date(get_app_root() + '/content/timeline.jsonl')
    monthly_bookmark_statuses = load_statuses_by_date(get_app_root() + '/content/bookmarks.jsonl')
    monthly_statuses = {**monthly_timeline_statuses, **monthly_bookmark_statuses}

    for monthly_content, score in compute_long_term_interests(recent_domain_count(monthly_statuses)).items():
        print(monthly_content + ' ' + str(score))

    # diversity = topic_diversity(statuses)
    # number_of_recommendations = 10
    # count_of_long_term_interests = round(number_of_recommendations * diversity)
    # print(count_of_long_term_interests)


def compute_current_interests(statuses):
    if statuses is None:
        return None

    sorted_statuses = sorted(statuses, key=lambda status_instance: status_instance.score, reverse=True)

    top = sorted_statuses[:10]
    top_interests = []
    for status in top:
        tags = set(status.text)
        if len(tags) > 0:
            domains = get_tag_domains(tags)
            top_interests.append((status, domains))

    return top_interests


def domain_frequency(statuses):
    if statuses is None:
        return None

    domain_frequencies = {}
    for status in statuses:
        tags = set(status.text)
        if len(tags) > 0:
            domains = get_tag_domains(tags)

            for domain in domains:
                if domain in domain_frequencies:
                    domain_frequencies[domain] = domain_frequencies[domain] + 1
                else:
                    domain_frequencies[domain] = 1

    return sorted(domain_frequencies.items(), key=operator.itemgetter(1), reverse=True)


def recent_domain_count(statuses):
    if statuses is None:
        return None

    count = 0
    content = []

    for year in list(reversed(list(statuses.keys()))):
        if count > 6:
            break

        for month in list(reversed(list(statuses[year].keys()))):
            if count > 6:
                break

            content.append(domain_frequency(statuses[year][month]))
            count = count + 1

    return content


def compute_long_term_interests(domain_frequencies):
    if domain_frequencies is None:
        return None

    domain_scores = {}
    base_weight = 0.1
    month_count = 0
    sum_of_weights = 0
    for domains in domain_frequencies:
        weight = (1 - (month_count * base_weight))
        sum_of_weights += weight
        month_count += 1

        for (domain, frequency) in domains:
            if domain in domain_scores:
                domain_scores[domain] = (frequency * weight) + domain_scores[domain]
            else:
                domain_scores[domain] = (frequency * weight)

    for domain in domain_scores.keys():
        domain_scores[domain] = domain_scores[domain] / sum_of_weights

    return domain_scores


def compute_community_interests():
    members = load_community_feed()

    # for member in members:
    #     print(member.id)
    #     print(member.content)
    #     print()

    community_interest_tree = cluster_community_members(members[:10])

    community_interest_tree.show()


# def topic_diversity(statuses):
#     if statuses is None:
#         return None
#
#     universal_tag_collection = []
#     for status in statuses:
#         tags = set(status.text)
#         if len(tags) > 0:
#             for tag in tags:
#                 if tag.topic:
#                     universal_tag_collection.append(tag)
#
#     new_tag_collection = []
#     for tag in universal_tag_collection:
#         if tag not in new_tag_collection:
#             print(tag.topic)
#             new_tag_collection.append(tag)
#
#     return len(new_tag_collection) / len(universal_tag_collection)


if __name__ == '__main__':
    compute_community_interests()
    # compute_community_interests()
    # compute_interests()
