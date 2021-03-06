import hashlib
from math import sqrt


class SocialNetworkFeed:
    def get_public_trends_feed(self, **coordinates):
        pass

    def get_user_timeline_feed(self):
        pass

    def get_bookmarks_feed(self):
        pass

    def get_followings_feed(self):
        pass

    def get_community_feed(self):
        pass


class SocialNetworkStatus:
    def __init__(self, text, score, native_identifier=None, created=None):
        self.id = native_identifier
        self.text = text
        self.created = created
        self.score = score

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if type(self.text) is str and type(other.text) is str:
                text_equals = (self.text == other.text)
                return text_equals
            elif type(self.text) is list and type(other.text) is list:
                absent = []
                if len(self.text) != len(other.text):
                    return False
                for item in self.text:
                    if item not in other.text:
                        absent.append(item)

                return len(absent) == 0

            return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class SocialNetworkTrend:
    def __init__(self, topic, score):
        self.topic = topic
        self.score = score

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.topic == other.topic:
                return True
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class SocialNetworkMember:
    def __init__(self, identifier, content):
        self.id = identifier
        self.content = content

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.id == other.id:
                return True
            else:
                return False
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return int(hashlib.sha1(self.id.encode('utf-8')).hexdigest(), 16) % (10 ** 8)

    def __str__(self):
        return self.id

    def default(self, o):
        return o.__dict__


class Tag:
    def __init__(self, topic, context=None, context_fraction=0):
        self.topic = topic
        self.context = context
        self.importance = context_fraction

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.topic is None or other.topic is None:
                return False

            topic_equals = (self.topic.lower() == other.topic.lower())

            type_key = 'description'
            type_equals = False
            if (type_key in self.context) & (type_key in other.context):
                type_equals = (self.context[type_key] == other.context[type_key])

            sub_type_key = 'sub_types'
            sub_type_equals = False
            if (sub_type_key in self.context) & (sub_type_key in other.context):
                if (self.context[sub_type_key] is None) and (other.context[sub_type_key] is None):
                    sub_type_equals = True
                elif (self.context[sub_type_key] is not None) and (other.context[sub_type_key] is not None):
                    sub_type_equals = (set(self.context[sub_type_key]) == set(other.context[sub_type_key]))

            return topic_equals & type_equals & sub_type_equals
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        if self.topic is None:
            return int(hashlib.sha1(''.lower().encode('utf-8')).hexdigest(), 16) % (10 ** 8)

        return int(hashlib.sha1(self.topic.lower().encode('utf-8')).hexdigest(), 16) % (10 ** 8)

    def __str__(self):
        if self.topic is None or self.context is None:
            if self.topic is None and self.context is not None:
                return '[No title] ' + str(self.context)
            elif self.topic is not None and self.context is None:
                return self.topic
            else:
                return ''

        return self.topic + ' ' + str(self.context)


class ZScore:
    def __init__(self, decay, past=None):
        if past is None:
            past = []
        self.sqrAvg = self.avg = 0

        # The rate at which the historic data's effect will diminish
        self.decay = decay

        for x in past:
            self.update(x)

    def update(self, value):
        # Set initial averages to the first value in the sequence
        if self.avg == 0 and self.sqrAvg == 0:
            self.avg = float(value)
            self.sqrAvg = float((value ** 2))
        # Calculate the average of the rest of the values using a floating average
        else:
            self.avg = self.avg * self.decay + value * (1 - self.decay)
            self.sqrAvg = self.sqrAvg * self.decay + (value ** 2) * (1 - self.decay)
        return self

    def standard_deviation(self):
        return sqrt(self.sqrAvg - self.avg ** 2)

    def get_score(self, obs):
        if self.standard_deviation() == 0:
            return (obs - self.avg) * float("infinity")
        else:
            return (obs - self.avg) / self.standard_deviation()
