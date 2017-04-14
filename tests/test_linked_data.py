import json
import os
import sys

try:
    sys.path.insert(0, os.path.realpath(os.environ['INTEREST_ENGINE_PATH']))
except KeyError:
    sys.stderr.write("Application Root environmental variable 'INTEREST_ENGINE_PATH' not set\n")
    sys.exit(1)
# from text_analysis.text_analytics import extract_entities
from social_networks.linked_data import get_ontology_data
from social_networks.updater import load_bookmarks, load_followings, load_timeline
from social_networks.utils import get_app_root, jdefault
from tests.models import TextTest
from tests.test_utils import calculate_f_measure, get_true_positives, get_false_positives, get_false_negatives, \
    calculate_precision, calculate_recall


def get_text_instance(text_instance):
    if text_instance is None:
        return None

    test_instance = {'Text': text_instance.text, 'Expected': text_instance.expected_output,
                     'Actual': text_instance.actual_output}
    return test_instance


def load_text_instance(text_content):
    if text_content is None:
        return None

    text_dict = json.loads(text_content)
    return TextTest(text=text_dict['Text'], expected=text_dict['Expected'], actual=text_dict['Actual'])


def load_social_network_data():
    bookmarks = load_bookmarks()
    followings = load_followings()
    timeline = load_timeline()

    collection = bookmarks + followings + timeline

    for item in collection:
        print(item.text)

    return collection


if __name__ == "__main__":
    with open(get_app_root() + '/tests/data/test-data.txt', 'r') as file:
        for line in file:
            test_case = load_text_instance(line)
            print(test_case.text)
            print()
            for keyword in test_case.actual_output:
                print(keyword)
                print(get_ontology_data(keyword))
                print()

            print()

    # true_positives = []
    # false_positives = []
    # false_negatives = []
    #
    # with open(get_app_root() + '/tests/data/test-data.txt', 'r') as file:
    #     for line in file:
    #         test_case = load_text_instance(line)
    #         true_positives.append(get_true_positives(test_case.expected_output, test_case.actual_output))
    #         false_positives.append(get_false_positives(test_case.expected_output, test_case.actual_output))
    #         false_negatives.append(get_false_negatives(test_case.expected_output, test_case.actual_output))
    #
    # true_positives = [tp for tp in true_positives if tp]
    # false_positives = [fp for fp in false_positives if fp]
    # false_negatives = [fn for fn in false_negatives if fn]
    #
    # print(true_positives)
    # print()
    # print(false_positives)
    # print()
    # print(false_negatives)
    # print(calculate_f_measure(calculate_precision(true_positives, false_positives),
    #                           calculate_recall(true_positives, false_negatives)))

    # texts = [
    #     TextTest(text="\" I've got my day job back \" Maria Sharapova is preparing to return to tennis after a 15 - "
    #                   "month ban :", expected=['Maria Sharapova', 'tennis']),
    #     TextTest(
    #         text="Zlatan Ibrahimovic : \" I m enjoying being at a a fantastic club , without doubts , one of the "
    #              "biggest clubs in the world", expected=['Zlatan Ibrahimovic']),
    #     TextTest(text="Mila Kunis opens up about life with two children", expected=['Mila Kunis']),
    #     TextTest(text="Rebecca Ferguson poses for photographers whilst promoting LIFE on SiriusXm ( 20.03 . 17 ) x",
    #              expected=['Rebecca Ferguson', 'LIFE', 'SiriusXm', '20.03 . 17']),
    #     TextTest(
    #         text="Reason 2 why I love Texans Cheer 2 . It's such an honor to work for the best in the biz . We love "
    #              "you Coach Alto ,",
    #         expected=['Texans Cheer', 'Coach Alto']),
    #     TextTest(text="Jose Mourinho has revealed the latest team news ahead of the weekend :",
    #              expected=['Jose Mourinho']),
    #     TextTest(text="Kendall and Paris are the new girl gang to watch :", expected=['Kendall', 'Paris']),
    #     TextTest(
    #         text="21 - year-old Sadeera Samarawickrama is the 2nd highest First-class run scorer in 2017 , how is he "
    #              "not in Sri Lanka squad.",
    #         expected=['Sadeera Samarawickrama', '2017', 'Sri Lanka']),
    #     TextTest(text="Throwback to Giggs and Evra's masterclass set piece MUFC", expected=['Giggs', 'Evra', 'MUFC']),
    #     TextTest(text="Check out the behind the scenes of my FIFA 17 shoot !", expected=['FIFA 17']),
    #     TextTest(text="Frances Bean Cobain defaced her own Marc Jacobs billboard with graffiti .",
    #              expected=['Frances Bean Cobain', 'Marc Jacobs']),
    #     TextTest(
    #         text="This Cristiano Ronaldo statue at the newly named Cristiano Ronaldo Airport in Madeira is absolutely "
    #              "dreadful .",
    #         expected=['Cristiano Ronaldo', 'Cristiano Ronaldo Airport', 'Madeira']),
    #     TextTest(text="March 28 - STX Films ' presentation at 2017 CinemaCon in Las Vegas . milakunis cinemacon",
    #              expected=['March 28', 'STX Films', '2017 CinemaCon', 'Las Vegas', 'milakunis', 'cinemacon']),
    #     TextTest(
    #         text="Parul Gulati:I can control my destiny , but not my fate . Destiny means there are opportunities to "
    #              "turn right or left , but fate is a one-way street . I believe we all have the choice as to whether "
    #              "we fulfil our destiny , but our fate is sealed . -Akshaykumar Upadhye GoodMorning",
    #         expected=['Parul Gulati', 'Akshaykumar Upadhye']),
    #     TextTest(
    #         text="Nicole Grimaudo:Nicole Grimaudo 's cover photo : Nicole Grimaudo posa per Sicilia Outlet Village",
    #         expected=['Nicole Grimaudo', 'Sicilia']),
    #     TextTest(text="Nicole Grimaudo:Nicole Grimaudo : Nicole posa per Torino Outlet Village",
    #              expected=['Nicole Grimaudo', 'Torino']),
    #     TextTest(
    #         text="Ghost In The Shell:Ghost In The Shell - 5 Days : In 5 days , revenge is coming . Get tickets now to "
    #              "see Ghost In The Shell in theatres , RealD 3D and IMAX 3D this Friday : fandan.co/2neYNWt. LIVE "
    #              "with Scarlett Johansson talking about her upcoming movie Ghost In The Shell",
    #         expected=['Ghost In The Shell', 'RealD 3D', 'IMAX 3D', 'Friday', 'Chica', 'Scarlett Johansson']),
    #     TextTest(
    #         text="Chloe Agnew:Atlanta Pops Orchestra : Atlanta Pops Orchestra is looking forward to our return to the "
    #              "beautiful Oxford Performing Arts Center on Friday night ! Join the Pops , Chloe Agnew , Irish tenor "
    #              "Dermot Kiernan , Riverdance alum Scott Porter and conductor Jason Altieri in a soaring evening of "
    #              "music with Agnew 's fan favorites , Irish fun , & much , much more !",
    #         expected=['Chloe Agnew', 'Atlanta Pops Orchestra', 'Oxford Performing Arts Center', 'Friday', 'Pops',
    #                   'Irish', 'Dermot Kiernan', 'Riverdance', 'Scott Porter', 'Jason Altieri', 'Agnew']),
    #     TextTest(text="Tomb Raider:SELF Magazine : Alicia Vikander is looking strong as hell in theses exclusive "
    #                   "photos from Warner Bros. Pictures . Tomb Raider Vikander 's famous trainer Magnus talks shop "
    #                   "about whipping the Tomb Raider into ship-shape ! Vanity Fair : The Oscar winner dons the "
    #                   "iconic tank top and embarks on a global adventure in the new film based on the video game . We "
    #                   "'re incredibly excited to share a first look at the talented Alicia Vikander as Lara Croft in "
    #                   "the upcoming Tomb Raider movie . I was asked to take on this role I got really Croft is a "
    #                   "truly iconic character , Vikander relayed to Vanity Fair via e-mail . think people can "
    #                   "identify with her for lots of different reasons , but for me I very much see her as a model "
    #                   "for many young women . '' Read more via Vanity Fair : vntyfr.com/XGqrpac",
    #              expected=['Tomb Raider', 'SELF Magazine', 'Alicia Vikander', 'Warner Bros. Pictures', 'Vikander',
    #                        'Magnus', 'Vanity Fair', 'Oscar', 'Lara Croft', 'Croft']),
    #     TextTest(text="Chris Evans Fangirls:[ Video ] Gifted : B-Roll , with Chris Evans , McKenna Grace , "
    #                   "Octavia Spencer , Jenny Slate . | Chris Evans Fangirls : Check out this new video for Gifted , "
    #                   "the upcoming movie of Chris Evans ! In this behind the scenes video we can see the main cast : "
    #                   "Chris Evans , McKenna Grace , Octavia Spencer and Jenny Slate , as well as the director , "
    #                   "Marc Webb . Only being released in select theaters in the USA on April 7th ( 2017 ) .",
    #              expected=['Chris Evans Fangirls', 'Gifted', 'B-Roll', 'Chris Evans', 'McKenna Grace',
    #                        'Octavia Spencer', 'Jenny Slate', 'Marc Webb', 'USA', 'April 7th ( 2017 )']),
    #     TextTest(text="Henry Cavill:Timeline Photos : I 'm very excited to announce that Alexandra Daddario will be "
    #                   "joining Sir Ben Kingsley and me on my latest project , Nomis . We begin shooting , "
    #                   "under the command of our talented director David Raymond , later this month . I ca n't wait to "
    #                   "go to Canada and freeze my butt off for the first time this winter ! Winter "
    #                   "Didn'tComeToFlorida So I'mGoingToWinter Nomis Sir Ben Kingsley Alexandra Daddario stingrayed",
    #              expected=['Henry Cavill', 'Alexandra Daddario', 'Sir Ben Kingsley', 'Nomis', 'David Raymond', 'Canada',
    #                        'Florida']),
    #     TextTest(
    #         text="Batman:DC Comics : Here 's how you can celebrate Batman Day tomorrow , including giveaways and "
    #              "comic shop events ! www.dccomics.com/batmanday",
    #         expected=['Batman', 'DC Comics', 'Batman Day']),
    #     TextTest(
    #         text="Victoria's Secret Fashion Show:Watch Bruno Mars ' Hot Performance At The Victoria 's Secret Fashion "
    #              "Show : The singer joined the models on the runway for two songs , belting out `` Chunky '' and `` "
    #              "24K Magic . '' Turns out Bruno Mars was just getting warmed up for Carpool Karaoke on The Late Late "
    #              "Show with James Corden .", expected=["Victoria's Secret Fashion Show", 'Bruno Mars', 'Chunky',
    #                                                    '24K Magic', 'Carpool Karaoke', 'James Corden']),
    #     TextTest(text="Lily Collins:Photos from Lily Collins 's post : My Barnes & Noble book signing experience in "
    #                   "three words : Shocking . Humbling . Epic . Thank you so so much to all of you who came out , "
    #                   "waited for hours , and supported ! It was incredibly inspiring to meet you . Here 's to living "
    #                   "life Unfiltered ... Epic Reads HarperCollins",
    #              expected=['Lily Collins', 'Barnes & Noble', 'HarperCollins']),
    #     TextTest(text="Daily Mail Sport : Cristiano Ronaldo now has his own airport . That questionable mould of him "
    #                   "though", expected=['Daily Mail Sport', 'Cristiano Ronaldo']),
    #     TextTest(text="Manchester United , Trolling Clubs since 1878 : Tag Liverpool fans Wuio",
    #              expected=['Manchester United', '1878', 'Liverpool']),
    #     TextTest(text="Hypable.com : The first Pirates of the Caribbean 5 reviews have arrived , and they 're really "
    #                   "good ! Critics are calling it the best movie since the first",
    #              expected=['Hypable.com', 'Pirates of the ', 'Caribbean 5']),
    #     TextTest(text="Hypable.com : The Avengers were not impressed with the new Justice League trailer !",
    #              expected=['Hypable.com', 'Avengers', 'Justice League']),
    #     TextTest(text="Daily Mail Sport : 14 years at FC Bayern Two years at Manchester United Bastian Schweinsteiger "
    #                   "is off !", expected=['Daily Mail Sport', 'FC Bayern', 'Manchester United',
    #                                         'Bastian Schweinsteiger']),
    #     TextTest(text="Manchester United by Fasnzone : Interviewer : '' What do you have to say Sir about the most "
    #                   "dominating clubs in the world right now ? '' Sir Alex Ferguson : '' Its the spanish teams "
    #                   "because they have got great players like Ronaldo and Messi..but this will change , "
    #                   "Ronaldo will get older , Messi will get older and English clubs will reign again..Everything "
    #                   "will be back like before '' Interviewer : '' So you mean to say Liverpool will rise again ? '' "
    #                   "Sir Alex Ferguson : '' I am talking about elite and dominating clubs . Small clubs do n't "
    #                   "compete ! '' Trademark Sir Alex Ferguson",
    #              expected=['Manchester United', 'Sir Alex Ferguson',
    #                        'spanish', 'Ronaldo', 'Messi', 'English', 'Liverpool'])
    # ]
    #
    # for text in texts:
    #     entities = extract_entities(text.text)
    #     text.actual_output = entities
    #     print(entities)
