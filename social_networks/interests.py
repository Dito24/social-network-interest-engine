import operator
import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.communities import get_matching_clusters
from social_networks.linked_data import get_tag_domains
from social_networks.updater import load_bookmarks, load_timeline, update_bookmarks, update_timeline
from social_networks.utils import get_app_root, load_statuses, load_statuses_by_date


def update_statuses():
    bookmarks = load_bookmarks()
    timeline = load_timeline()

    update_bookmarks(bookmarks)
    update_timeline(timeline)


def compute_current_interests():
    # update_statuses()

    timeline = load_statuses(get_app_root() + '/content/timeline.jsonl')
    # followings = load_followings()
    bookmarks = load_statuses(get_app_root() + '/content/bookmarks.jsonl')

    # 0.5 weight for the timeline content
    for status in timeline:
        status.score = 0.5 * status.score

    # 0.25 weight for bookmarks content
    for status in bookmarks:
        status.score = 0.25 * status.score

    # 0.25 weight for followings content
    # for status in followings:
    #     status.score = 0.25 * status.score

    # statuses = bookmarks + followings + timeline
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

    # statuses = bookmarks + timeline
    sorted_statuses = sorted(final, key=lambda status_instance: status_instance.score, reverse=True)

    top = sorted_statuses[:33]
    top_interests = []
    for status in top:
        tags = set(status.text)
        if len(tags) > 0:
            domains = get_tag_domains(tags)
            top_interests.append((status, domains))

    print(len(sorted_statuses))

    return top_interests


def compute_long_term_interests():
    # update_statuses()

    monthly_timeline_statuses = load_statuses_by_date(get_app_root() + '/content/timeline.jsonl')
    monthly_bookmark_statuses = load_statuses_by_date(get_app_root() + '/content/bookmarks.jsonl')
    monthly_statuses = {**monthly_timeline_statuses, **monthly_bookmark_statuses}

    domain_frequencies = recent_domain_count(monthly_statuses)

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


def compute_community_interests():
    clusters = get_matching_clusters()

    members = {}
    for topic, cluster in clusters.items():
        for member in cluster:
            if member not in members:
                members[member] = member.content

            filtered = []
            for tag in members[member]:
                sub_types = tag.context['sub_types']
                if len(sub_types) > 0:
                    if sub_types[len(sub_types) - 1] != topic:
                        filtered.append(tag)

            members[member] = filtered

    return members


if __name__ == '__main__':
    for interest in compute_current_interests():
        tag_collection = interest[0].text
        tag_list = []
        for tag in tag_collection:
            tag_list.append(tag.original)

        print(str(set(tag_list)) + ' points: ' + str(interest[0].score))
    # for user, items in compute_community_interests().items():
    #     print(user)
    #     for item in items:
    #         print(item.topic)
    #     print()
