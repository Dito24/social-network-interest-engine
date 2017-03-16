import math
import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from social_networks.concepts import SocialNetworkStatus
from feed_facebook.text_refinement import refine_facebook_post


def convert_posts_to_native_statuses(status_data, graph):
    if status_data is None:
        return []

    statuses = []
    for status in status_data:
        content = ''
        if 'name' in status:
            if status['name'] is not None:
                content += (status['name'] + ': ')

        if 'description' in status:
            content += (status['description'] + ' ')

        if 'message' in status:
            content += status['message']

        if content is None:
            continue

        score = 0
        if graph is not None:
            if 'parent_id' in status:
                score = get_post_score(get_post_reactions(status['parent_id'], graph),
                                       get_post_shares(status['parent_id'], graph))

        statuses.append(SocialNetworkStatus(native_identifier=status['id'], text=refine_facebook_post(content),
                                            created=status['updated_time'], score=score))

    return statuses


def get_post_reactions(post_id, graph):
    if not (post_id, graph):
        return None

    reactions = {}

    arguments = [
        'reactions.type(LIKE).limit(0).summary(true).as(like)', 'reactions.type(LOVE).limit(0).summary(true).as(love)',
        'reactions.type(WOW).limit(0).summary(true).as(wow)']
    arguments = ",".join(arguments)

    response = graph.request(
        graph.version + '/' + post_id, args={'access_token': graph.access_token, 'fields': arguments})

    for reaction_type, result in response.items():
        if reaction_type == 'id':
            continue

        reactions[reaction_type] = (result['summary'])['total_count']

    return reactions


def get_post_shares(post_id, graph):
    if not post_id:
        return None

    response = graph.get_object(post_id, fields='shares')

    if 'shares' in response:
        return response['shares']['count']
    else:
        return None


def get_post_score(reactions, shares):
    if reactions is None or shares is None:
        return None

    if shares < 0:
        return None

    weigh_like = 1
    weigh_love = 1.5
    weigh_wow = 2
    weigh_share = 10

    total = 0
    if 'like' in reactions:
        likes = reactions['like']
        if likes and likes > 0:
            total += (likes * weigh_like)

    if 'love' in reactions:
        love = reactions['love']
        if love and love > 0:
            total += (love * weigh_like)

    if 'wow' in reactions:
        wow = reactions['wow']
        if wow and wow > 0:
            total += (wow * weigh_wow)

    total += (shares * weigh_share)

    base_score = total / (weigh_like + weigh_love + weigh_wow + weigh_share)

    return math.log(max(base_score, 1))


def get_status_index(statuses, identifier):
    if statuses is None:
        return None

    index = 0
    while index < len(statuses):
        status = statuses[index]

        if status.id == identifier:
            return index

        index += 1

    return None
