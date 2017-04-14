import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
from text_analysis.text_analytics import extract_entities, get_entity_frequency
from tests.test_utils import get_true_positives, get_false_positives, get_false_negatives, calculate_precision, \
    calculate_recall, calculate_f_measure

doc1 = 'Labour should be prepared to alter its stance on Brexit - and if necessary argue that Britain should stay ' \
       'inside the EU, Tony Blair has said. The former PM told the BBC\'s Andrew Marr that Labour should change its ' \
       'position if the government delivers a Brexit deal the people do not like. He urged Labour to hold ministers ' \
       'to account over its pledge to secure a trade deal with the EU. Labour\'s Jeremy Corbyn has said the ' \
       'referendum result should be respected. Mr Blair, who was Labour prime minister between 1997 and 2007, ' \
       'said the government faced negotiations of "unparalleled complexity" if it was to achieve its stated aim of ' \
       'delivering an agreement that replicates as closely as possible Britain\'s existing trade arrangements with ' \
       'the EU. While voters had backed Brexit in last year\'s referendum, he said he believed it was "possible" the ' \
       'public mood would change if it did not result in the promised benefits - and Labour should be ready to ' \
       'capitalise on that. '
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
doc5 = "According to the Journal of Agricultural and Food Technology, adding a 140g serving of purple potatoes twice " \
       "a day to the diet of overweight, middle-aged subjects caused their blood pressure to drop almost five points " \
       "within just a month – despite the fact that almost 80% of them were already on antihypotensive drugs. Such a " \
       "fall could “decrease the risk of stroke by 34% and of heart disease by 21%” according to Barts and The London " \
       "School of Medicine. These potatoes added 280 calories to their daily diet, but the subjects in this trial " \
       "didn’t gain weight either. OK, this may be just one study and we need a lot more research before solid " \
       "conclusions can be drawn, but these results do contribute to a growing weight of evidence behind the benefits " \
       "of going for purple. As these varieties are widely sold in the seed catalogues yet are still a rare find in " \
       "the shops, to me it makes the case for picking them over the ubiquitous white ones a pretty strong one. "
doc6 = "Government policy interventions aimed at solving inequality would not produce results if the country’s " \
       "dysfunctional education system wasn’t fixed. This was what Stellenbosch University economics professor " \
       "Servaas van der Berg told delegates at a two-day conference in Pretoria organised by the Programme to Support " \
       "Pro-Poor Policy Development in the presidency’s department of planning, monitoring and evaluation in " \
       "partnership with the EU. Van der Berg was among academics and civil society groups who presented studies to " \
       "policymakers on the National Development Plan agenda to reduce poverty and eliminate inequality by 2030. The " \
       "research work was supported by grant funding sourced through a partnership between government and the EU. "
doc7 = 'Top finance officials including new U.S. Treasury Secretary Steven Mnuchin are debating what stance to take ' \
       'on free trade at a meeting that will help set the tone for the global economy. The gathering of finance ' \
       'ministers and central bank heads from the Group of 20 countries has focused on shifting attitudes toward ' \
       'trade, particularly after U.S. President Donald Trump vowed to impose border taxes and rewrite free trade ' \
       'deals he says have shortchanged the U.S. Mnuchin has said trade needs to be "fair," which would be a step ' \
       'back from the group\'s previous blanket condemnation of trade barriers. Attention at the two-day meeting in ' \
       'the German spa town of Baden-Baden has centered on a joint statement that is being prepared for Saturday. ' \
       'Early drafts have dropped an earlier ban on protectionism, but there was no agreement on what would replace ' \
       'it, said officials who briefed reporters Friday on condition of anonymity because the talks were ongoing. The ' \
       'meeting\'s host, German Finance Minister Wolfgang Schaeuble, told reporters that the discussion was about ' \
       '"the right formulation regarding the openness of the world economy." The last such gathering, in July 2016 in ' \
       'Chengdu, China, issued a strong statement in favor of free trade, saying "we will resist all forms of ' \
       'protectionism." Possible replacements include support for \"fairness.\" '

TEST_DATA = [[doc1, ['Labour', 'Brexit', 'Britain', 'EU', 'Tony Blair', 'BBC', 'Andrew Marr', 'Jeremy Corbyn']],
             [doc2, ['Britain First', 'Donald Trump', 'far-right group', 'Paul Golding',
                     'Jayda Fransen', 'Telford', 'Shropshire', 'anti-Muslim', 'Muslim', 'Union Jack',
                     'Rule Britannia', 'Unite Against Facism']],
             [doc3, ['Jose Mourinho', 'EFL Cup', 'Wembley', 'Chelsea', 'Southampton', 'Manchester United',
                     'Portuguese', 'London', 'Stockport']],
             [doc4, ['Academy Awards', 'Oscars', 'La La Land', 'Alien: Covenant', 'Last Supper',
                     'Michael Fassbender', 'Android', 'James Franco', 'Ridley Scott', 'Disney',
                     'Beauty and the Beast', 'Belle', 'Emma Watson', 'King Arthur: Legend of the Sword',
                     'Russell Crowe', 'Robin Hood']],
             [doc5, ['Journal of Agricultural and Food Technology', 'antihypotensive', 'Barts',
                     'The London School of Medicine']],
             [doc6, ['Stellenbosch University', 'Servaas van der Berg', 'Pretoria', 'Pro-Poor Policy Development',
                     'EU', 'National Development Plan']],
             [doc7, ['U.S. Treasury', 'Steven Mnuchin', 'U.S.', 'Donald Trump', 'Mnuchin', 'German',
                     'Baden-Baden', 'Wolfgang Schaeuble', 'Chengdu', 'China']]
             ]


# unit tests for entity frequency
def test_entity_frequency_one():
    test_text = doc1
    test_entities = TEST_DATA[0][1]
    expected_output = {
        'Labour': 6, 'Brexit': 3, 'Britain': 2, 'EU': 3, 'Tony Blair': 2, 'BBC': 1, 'Andrew Marr': 1, 'Jeremy Corbyn': 1
    }

    assert get_accuracy_percentage(get_entity_frequencies(test_text, test_entities), expected_output) >= 0.75


def test_entity_frequency_two():
    test_text = doc2
    test_entities = TEST_DATA[1][1]
    expected_output = {
        'Britain First': 2, 'Donald Trump': 2, 'far-right group': 2, 'Paul Golding': 1, 'Jayda Fransen': 1,
        'Telford': 3, 'Shropshire': 1, 'anti-Muslim': 1, 'Muslim': 1, 'Union Jack': 1, 'Rule Britannia': 1,
        'Unite Against Facism': 1
    }

    assert get_accuracy_percentage(get_entity_frequencies(test_text, test_entities), expected_output) >= 0.75


def test_entity_frequency_three():
    test_text = doc3
    test_entities = TEST_DATA[2][1]
    expected_output = {
        'Jose Mourinho': 3, 'EFL Cup': 1, 'Wembley': 1, 'Chelsea': 1, 'Southampton': 1, 'Manchester United': 1,
        'Portuguese': 1, 'London': 1, 'Stockport': 1
    }

    assert get_accuracy_percentage(get_entity_frequencies(test_text, test_entities), expected_output) >= 0.75


def test_entity_frequency_four():
    test_text = doc4
    test_entities = TEST_DATA[3][1]
    expected_output = {
        'Academy Awards': 1, 'Oscars': 1, 'La La Land': 1, 'Alien: Covenant': 3, 'Last Supper': 1,
        'Michael Fassbender': 1, 'Android': 1, 'James Franco': 1, 'Ridley Scott': 1, 'Disney': 1,
        'Beauty and the Beast': 1, 'Belle': 1, 'Emma Watson': 1, 'King Arthur: Legend of the Sword': 2,
        'Russell Crowe': 1, 'Robin Hood': 1
    }

    assert get_accuracy_percentage(get_entity_frequencies(test_text, test_entities), expected_output) >= 0.75


def get_entity_frequencies(text, terms):
    if text is None or terms is None:
        return None

    entity_frequencies = {}
    for term in terms:
        entity_frequencies[term] = get_entity_frequency(term, text)

    return entity_frequencies


def get_accuracy_percentage(entity_frequencies, expected):
    if entity_frequencies is None or expected is None:
        return None

    copy = dict(expected)
    original = len(copy)
    for term, frequency in expected.items():
        if term in copy:
            if entity_frequencies[term] != frequency:
                del copy[term]

    return len(copy) / original


if __name__ == "__main__":
    print(extract_entities("\" I've got my day job back \" Maria Sharapova is preparing to return to tennis after a "
                           "15 - month ban :"))
    print(extract_entities("21 - year-old Sadeera Samarawickrama is the 2nd highest First-class run scorer in 2017 , "
                           "how is he not in Sri Lanka squad."))
    # true_positives = []
    # false_positives = []
    # false_negatives = []
    #
    # for item in TEST_DATA:
    #     entities = extract_entities(item[0])
    #
    #     true_positives.append(get_true_positives(item[1], entities))
    #     false_positives.append(get_false_positives(item[1], entities))
    #     false_negatives.append(get_false_negatives(item[1], entities))
    #
    # print(true_positives)
    # print()
    # print(false_positives)
    # print()
    # print(false_negatives)
    # print()
    # print(calculate_f_measure(calculate_precision(true_positives, false_positives),
    #                           calculate_recall(true_positives, false_negatives)))
