import os
import sys

from difflib import SequenceMatcher
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.util import ngrams

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from text_analysis.alchemyapi import AlchemyAPI

# external named entity recognition service connection instance
NER_SERVICE = AlchemyAPI()


def extract_entities(text):
    if text is None:
        return None

    response = NER_SERVICE.entities('text', text)

    entities = []
    if response['status'] == 'OK':
        for entity in response['entities']:
            if 'type' in entity:
                if entity['type'] == 'Quantity':
                    continue
            entities.append(entity['text'])
    else:
        print('Error in entity extraction call: ', response['statusInfo'])
        return []

    return list(set(entities))


def get_entity_fractions(entities, text):
    if not entities:
        return []

    if not text:
        return []

    frequencies = []
    total_frequencies = 0
    for entity in entities:
        frequency = get_entity_frequency(entity, text)
        frequencies.append({'entity': entity, 'frequency': frequency})
        total_frequencies += frequency

    fractions = []
    for entry in frequencies:
        entity = entry['entity']

        if total_frequencies > 0:
            fraction = entry['frequency'] / total_frequencies
        else:
            fraction = 0
        fractions.append({'entity': entity, 'fraction': fraction})

    return fractions


def get_entity_frequency(entity, text):
    if not (entity, text):
        return 0

    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(entity)
    tokens = [word for word in tokens if word not in stop_words]

    sequences = []
    for number in range(1, len(tokens) + 1):
        n_grams = ngrams(tokens, number)

        for item in n_grams:
            word = ' '.join(item)
            frequency = text.count(word)

            if frequency > 0:
                sequences.append({'sequence': word, 'frequency': frequency})

    index = 0
    for item in sequences:
        if not (item['sequence'] == entity):
            count = item['frequency'] - text.count(entity)
            sequences[index]['frequency'] = count

        index += 1

    total = 0
    for sequence in sequences:
        total += sequence['frequency']

    return total


def calculate_word_similarity(original, retrieved):
    if original is None or retrieved is None:
        return None

    return SequenceMatcher(None, original, retrieved).ratio()


if __name__ == "__main__":
    doc1 = 'It is only two months since Henrikh Mkhitaryan was the man in the same position Anthony Martial ' \
           'currently finds himself in. Held accountable for a poor workrate in the derby defeat to Manchester City ' \
           'in September, Mkhitaryan had to take the long road back into Jose Mourinho’s plans. Mkhitaryan is ' \
           'a great player. Martial must learn from Mkhitaryan. Hail Henrikh Mkhitaryan. Come one Henrikh!!! ' \
           'European Organization for Nuclear Research is a great place to be. Anthony Martial has been to the ' \
           'Nuclear Research center.'
    doc2 = "Three men have been arrested after Britain First members marched through a town centre, including one " \
           "supporter wearing a Donald Trump mask. The far-right group's leader Paul Golding and his deputy Jayda " \
           "Fransen joined protesters as they met in Telford, Shropshire on Saturday afternoon. More than 150 " \
           "supporters marched from the town's train station to a nearby council building where they held a rally " \
           "with anti-Muslim speeches. The group said they were in Telford to expose 'Muslim grooming gangs' which " \
           "they claim have been covered up by the authorities. Supporters, including one man who was wearing a " \
           "heavily-tanned Donald Trump mask, waved Union Jack flags and sang 'Rule Britannia' during the march. " \
           "There was a heavy police presence in Telford as a counter protest by Unite Against Facism was organised " \
           "close to the scene of the Britain First rally. "
    doc3 = "Jose Mourinho says he can't wait for Sunday's EFL Cup final as he relishes the prospect of a new landmark " \
           "in his career at Wembley. Mourinho won the competition on three occasions while in charge at Chelsea, " \
           "and would become the first-ever Manchester United boss to win a trophy in his opening season if he can " \
           "guide his side to victory over Southampton on Sunday. Before the Portuguese and his squad set off for " \
           "London from Stockport Station on Saturday afternoon - club suits in-hand - Mourinho revealed his " \
           "eagerness to get the game underway. "
    doc4 = "This year’s Academy Awards edition is almost here, which means movie fans will probably be busy counting " \
           "how many Oscars La La Land ends up getting. But that doesn’t mean we don’t have fresh trailers for you. " \
           "In fact, there are plenty of great clips worth checking out, including an extensive preview of Alien: " \
           "Covenant. We talked about this first Alien: Covenant extensive prologue earlier this week. Aptly titled " \
           "Last Supper, the clip shows us the various characters of the movie that will likely be consumed by a " \
           "certain type of parasite. You know, the alien kind. Michael Fassbender, who plays an Android, " \
           "will probably keep surviving. James Franco also plays the kind of character that might make it into the " \
           "next Alien episode. The first new Ridley Scott movie opens on May 19th. Disney released a new clip for " \
           "its upcoming Beauty and the Beast, a movie everyone and their grandmother will probably see this March. " \
           "Meet Belle in this one, or Emma Watson singing. This is not your average, romanticized version of King " \
           "Arthur: Legend of the Sword. Instead, it’s a movie that feels more real. Just like Russell Crowe’s 2010 " \
           "Robin Hood. The new King Arthur movie comes out on May 12th."

    # print('entities')
    # print(extract_entities(doc1))
    # print(extract_entities(doc2))
    # print(extract_entities(doc3))
    # print(extract_entities(doc4))

    # print('Henrikh Mkhitaryan:' + str(entity_frequency('Henrikh Mkhitaryan', doc1)))
    # print('Jose Mourinho:' + str(entity_frequency('Jose Mourinho', doc3)))
    # print('Jose Mourinho:' + str(entity_frequency('Jose Mourinho', doc1)))
    # print('European Organization for Nuclear Research:' +
    #       str(entity_frequency('European Organization for Nuclear Research', string)))
    # print('Anthony Martial:' + str(entity_frequency('Anthony Martial', string)))
    # print('Jayasuriya:' + str(entity_frequency('Jayasuriya', string)))

    # print(entity_frequency('Jose Mourinho', doc3))
    # print(str(get_idf('Jose Mourinho', doc3)))

    # print(entity_frequency('Henrikh Mkhitaryan', doc1))
    # print(str(get_idf('Henrikh Mkhitaryan', doc1)))

    print(calculate_word_similarity('Manchester United', 'Manchester United F.C. Reserves and '
                                                         'Academy'))
    print(calculate_word_similarity('manchester united reserves and academy', 'Manchester United F.C. Reserves and '
                                                                              'Academy'))
    print(calculate_word_similarity('manchester united', 'Manchester United F.C. Reserves and '
                                                                              'Academy'))

    print(calculate_word_similarity('Manchester United', 'Manchester United F.C.'))
    print(calculate_word_similarity('manchester united', 'Manchester United F.C.'))
    print()
    print(calculate_word_similarity('European Organization for Nuclear Research', 'CERN'))
    print(calculate_word_similarity('European Organization for Nuclear Research', 'UNESCO'))
    print(calculate_word_similarity('European Organization for Nuclear Research', 'Nuclear Energy Agency'))
