def get_true_positives(expected, actual):
    if expected is None or actual is None:
        return None

    true_positives = []
    for actual_entity in actual:
        if actual_entity in expected:
            true_positives.append(actual_entity)

    return true_positives


def get_false_positives(expected, actual):
    if expected is None or actual is None:
        return None

    copy_of_identified_entities = actual[:]
    for actual_entity in actual:
        if actual_entity in expected:
            copy_of_identified_entities.remove(actual_entity)

    return copy_of_identified_entities


def get_false_negatives(expected, actual):
    if expected is None or actual is None:
        return None

    copy_of_expected_entities = expected[:]
    for actual_entity in actual:
        if actual_entity in expected:
            copy_of_expected_entities.remove(actual_entity)

    return copy_of_expected_entities


def calculate_precision(true_positives, false_positives):
    if true_positives is None or false_positives is None:
        return None

    precision = len(true_positives) / (len(true_positives) + len(false_positives))
    return precision


def calculate_recall(true_positives, false_negatives):
    if true_positives is None or false_negatives is None:
        return None

    recall = len(true_positives) / (len(true_positives) + len(false_negatives))
    return recall


def calculate_f_measure(precision, recall):
    if precision is None or recall is None:
        return None

    # assuming alpha is equal to 1/2
    if (precision + recall) == 0:
        return 0

    f_measure = (2 * precision * recall) / (precision + recall)
    return f_measure
