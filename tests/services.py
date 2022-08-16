from typing import OrderedDict


class TestOneScores:
    feature_a = {1, 8, 15, 17, 42, 46, 52, 58, 83, 87, 93, 96, 124, 128, 131, 138, 165, 169, 173, 176}
    feature_b = {21, 27, 33, 36, 62, 68, 71, 78, 101, 106, 113, 116, 141, 148, 151, 158, 181, 188, 192, 196}
    feature_c = {2, 6, 11, 18, 43, 47, 53, 56, 81, 86, 91, 97, 122, 130, 132, 136, 164, 166, 171, 177}
    feature_d = {22, 26, 32, 40, 61, 67, 73, 76, 102, 108, 111, 117, 142, 146, 153, 156, 184, 186, 191, 197}
    feature_e = {3, 7, 12, 16, 41, 48, 51, 57, 85, 90, 92, 99, 121, 127, 134, 137, 162, 168, 175, 179}
    feature_f = {23, 29, 31, 38, 65, 66, 72, 79, 103, 107, 114, 120, 145, 147, 154, 159, 185, 187, 195, 199}
    feature_g = {4, 10, 13, 20, 45, 49, 55, 60, 82, 89, 95, 100, 123, 126, 133, 140, 161, 167, 172, 180}
    feature_h = {24, 30, 35, 37, 63, 70, 74, 80, 105, 109, 115, 119, 143, 150, 152, 152, 157, 182, 189, 194, 198}
    feature_i = {5, 9, 14, 19, 44, 50, 54, 59, 84, 88, 94, 98, 125, 129, 135, 139, 163, 170, 174, 178}
    feature_j = {25, 28, 34, 39, 64, 59, 75, 77, 104, 110, 112, 118, 144, 149, 155, 160, 183, 190, 193, 200}

    scores = {
        '1': (2, 4, 6),
        '2': (6, 5, 3),
        '3': (6, 4, 3),
        '4': (3, 4, 6),
        '5': (4, 4, 5),
        '6': (3, 3, 6),
        '7': (3, 4, 5),
        '8': (2, 4, 5),
        '9': (3, 4, 4),
        '10': (5, 4, 4),

        '11': (3, 4, 5),
        '12': (2, 4, 6),
        '13': (5, 4, 3),
        '14': (2, 4, 5),
        '15': (3, 3, 6),
        '16': (3, 4, 4),
        '17': (2, 4, 5),
        '18': (2, 6, 6),
        '19': (5, 3, 3),
        '20': (5, 5, 3),

        '21': (2, 3, 6),
        '22': (1, 5, 6),
        '23': (5, 4, 3),
        '24': (3, 5, 6),
        '25': (3, 1, 5),
        '26': (2, 3, 6),
        '27': (5, 4, 4),
        '28': (6, 2, 2),
        '29': (6, 3, 3),
        '30': (3, 4, 6),

        '31': (5, 4, 4),
        '32': (2, 4, 6),
        '33': (6, 5, 3),
        '34': (6, 3, 3),
        '35': (5, 5, 2),
        '36': (3, 5, 6),
        '37': (3, 4, 6),
        '38': (4, 4, 5),
        '39': (3, 4, 5),
        '40': (2, 3, 5),

        '41': (6, 4, 4),
        '42': (5, 3, 3),
        '43': (4, 4, 5),
        '44': (2, 3, 6),
        '45': (3, 4, 5),
        '46': (3, 3, 5),
        '47': (2, 5, 6),
        '48': (3, 4, 5),
        '49': (6, 4, 4),
        '50': (4, 4, 3),

        '51': (5, 4, 2),
        '52': (3, 4, 4),
        '53': (3, 4, 6),
        '54': (6, 3, 3),
        '55': (2, 5, 6),
        '56': (5, 3, 3),
        '57': (5, 4, 4),
        '58': (6, 3, 3),
        '59': (1, 3, 5),
        '60': (2, 5, 6),

        '61': (2, 4, 6),
        '62': (5, 4, 4),
        '63': (5, 4, 4),
        '64': (2, 2, 6),
        '65': (4, 4, 5),
        '66': (6, 4, 3),
        '67': (2, 4, 5),
        '68': (6, 4, 3),
        '69': (6, 3, 3),
        '70': (4, 4, 5),

        '71': (3, 5, 6),
        '72': (3, 4, 4),
        '73': (2, 4, 5),
        '74': (2, 4, 6),
        '75': (5, 3, 3),
        '76': (1, 3, 6),
        '77': (6, 2, 2),
        '78': (2, 5, 6),
        '79': (5, 4, 3),

        '80': (6, 3, 3),
        '81': (6, 3, 3),
        '82': (3, 4, 6),
        '83': (3, 3, 6),
        '84': (6, 3, 2),
        '85': (6, 3, 3),
        '86': (2, 4, 6),
        '87': (3, 3, 5),
        '88': (5, 4, 3),
        '89': (2, 5, 6),
        '90': (3, 3, 5),

        '91': (3, 4, 6),
        '92': (3, 4, 4),
        '93': (5, 3, 3),
        '94': (5, 4, 4),
        '95': (3, 4, 5),
        '96': (6, 4, 2),
        '97': (5, 5, 3),
        '98': (4, 4, 5),
        '99': (2, 4, 5),
        '100': (4, 3, 1),

        '101': (5, 4, 4),
        '102': (2, 3, 5),
        '103': (4, 4, 6),
        '104': (2, 3, 6),
        '105': (6, 4, 3),
        '106': (2, 3, 7),
        '107': (2, 3, 6),
        '108': (3, 4, 5),
        '109': (3, 4, 5),
        '110': (5, 4, 4),

        '111': (2, 4, 5),
        '112': (6, 2, 2),
        '113': (6, 4, 3),
        '114': (6, 4, 3),
        '115': (3, 4, 6),
        '116': (6, 4, 3),
        '117': (3, 4, 5),
        '118': (7, 2, 2),
        '119': (5, 4, 3),
        '120': (5, 4, 3),

        '121': (4, 4, 5),
        '122': (3, 4, 6),
        '123': (5, 4, 3),
        '124': (2, 3, 6),
        '125': (1, 3, 4),
        '126': (4, 4, 6),
        '127': (5, 4, 4),
        '128': (3, 4, 6),
        '129': (2, 5, 6),
        '130': (3, 5, 6),

        '131': (5, 3, 2),
        '132': (2, 4, 6),
        '133': (6, 4, 3),
        '134': (4, 4, 3),
        '135': (2, 4, 5),
        '136': (3, 5, 5),
        '137': (3, 3, 6),
        '138': (5, 3, 3),
        '139': (5, 4, 4),
        '140': (2, 5, 6),

        '141': (2, 5, 6),
        '142': (1, 3, 5),
        '143': (2, 4, 6),
        '144': (5, 4, 3),
        '145': (5, 5, 3),
        '146': (1, 3, 5),
        '147': (6, 4, 4),
        '148': (3, 4, 6),
        '149': (3, 5, 5),
        '150': (2, 5, 6),

        '151': (2, 5, 6),
        '152': (6, 5, 3),
        '153': (2, 4, 6),
        '154': (3, 3, 5),
        '155': (7, 1, 1),
        '156': (6, 4, 2),
        '157': (7, 5, 2),
        '158': (5, 5, 3),
        '159': (5, 4, 2),
        '160': (2, 2, 6),

        '161': (2, 5, 6),
        '162': (6, 4, 3),
        '163': (5, 4, 4),
        '164': (5, 5, 2),
        '165': (6, 3, 3),
        '166': (3, 3, 6),
        '167': (6, 4, 2),
        '168': (6, 4, 3),
        '169': (2, 3, 6),
        '170': (3, 4, 5),

        '171': (3, 3, 6),
        '172': (3, 4, 6),
        '173': (6, 3, 2),
        '174': (5, 4, 3),
        '175': (0, 1, 5),
        '176': (2, 2, 6),
        '177': (6, 4, 4),
        '178': (5, 3, 3),
        '179': (0, 1, 5),
        '180': (3, 5, 6),

        '181': (3, 3, 6),
        '182': (3, 4, 6),
        '183': (2, 4, 6),
        '184': (3, 4, 6),
        '185': (6, 6, 3),
        '186': (1, 3, 5),
        '187': (3, 3, 5),
        '188': (2, 2, 6),
        '189': (3, 5, 5),
        '190': (6, 2, 2),

        '191': (1, 4, 5),
        '192': (2, 4, 6),
        '193': (5, 4, 3),
        '194': (4, 5, 6),
        '195': (6, 4, 2),
        '196': (2, 5, 6),
        '197': (2, 4, 5),
        '198': (2, 5, 6),
        '199': (0, 3, 5),
        '200': (5, 3, 3),
    }


class TestTwoAnswers:
    A = {
        '1': 'c',
        '2': 'c',
        '3': 'd',
        '4': 'd',
        '5': 'c',
        '6': 'e',
        '7': 'c',
        '8': 'a',
        '9': 'd',
        '10': 'c',

        '11': 'e',
        '12': 'e',
        '13': 'b',
        '14': 'd',
        '15': 'd',
        '16': 'c',
        '17': 'b',
        '18': 'a',
        '19': 'd',
        '20': 'e',

        '21': 'd',
        '22': 'e',
        '23': 'c',
        '24': 'c',
        '25': 'c',
        '26': 'd',
        '27': 'b',
        '28': 'e',
        '29': 'e',
        '30': 'c',

        '31': 'a',
        '32': 'd',
        '33': 'b',
        '34': 'c',
        '35': 'c',
        '36': 'c',
        '37': 'b',
        '38': 'c',
        '39': 'b',
        '40': 'c',

        '41': 'c',
        '42': 'd',
        '43': 'b',
        '44': 'c',
        '45': 'c',
        '46': 'd',
        '47': 'c',
        '48': 'b',
        '49': 'd',
        '50': 'd',

        '51': 'd',
        '52': 'e',
        '53': 'd',
        '54': 'c',
        '55': 'd',
        '56': 'b',
        '57': 'b',
        '58': 'c',
        '59': 'c',
        '60': 'd',

        '61': 'c',
        '62': 'b',
        '63': 'c',
        '64': 'b',
        '65': 'a',
        '66': 'c',
        '67': 'd',
        '68': 'a',
        '69': 'c',
        '70': 'c',

        '71': 'b',
        '72': 'b',
        '73': 'd',
        '74': 'b',
        '75': 'c',
        '76': 'a',
        '77': 'c',
        '78': 'c',
        '79': 'd',
        '80': 'c',
    }

    B = {
        '1': 'c',
        '2': 'd',
        '3': 'd',
        '4': 'c',
        '5': 'c',
        '6': 'c',
        '7': 'd',
        '8': 'a',
        '9': 'b',
        '10': 'c',

        '11': 'c',
        '12': 'c',
        '13': 'c',
        '14': 'c',
        '15': 'd',
        '16': 'b',
        '17': 'b',
        '18': 'c',
        '19': 'b',
        '20': 'e',

        '21': 'b',
        '22': 'b',
        '23': 'c',
        '24': 'b',
        '25': 'a',
        '26': 'c',
        '27': 'b',
        '28': 'c',
        '29': 'c',
        '30': 'a',

        '31': 'e',
        '32': 'a',
        '33': 'c',
        '34': 'c',
        '35': 'c',
        '36': 'c',
        '37': 'b',
        '38': 'c',
        '39': 'e',
        '40': 'b',

        '41': 'b',
        '42': 'b',
        '43': 'd',
        '44': 'c',
        '45': 'b',
        '46': 'b',
        '47': 'a',
        '48': 'e',
        '49': 'b',
        '50': 'a',

        '51': 'b',
        '52': 'd',
        '53': 'c',
        '54': 'd',
        '55': 'c',
        '56': 'c',
        '57': 'c',
        '58': 'c',
        '59': 'd',
        '60': 'e',

        '61': 'c',
        '62': 'b',
        '63': 'd',
        '64': 'b',
        '65': 'd',
        '66': 'c',
        '67': 'd',
        '68': 'c',
        '69': 'b',
        '70': 'e',

        '71': 'd',
        '72': 'b',
        '73': 'c',
        '74': 'd',
        '75': 'c',
        '76': 'c',
        '77': 'c',
        '78': 'd',
        '79': 'd',
        '80': 'c',
    }


class TestFourGroups:
    group_1 = {1, 2, 3, 4, 22, 23, 24, 25, 43, 44, 45, 46, 64, 65, 66, 67, 85, 86, 87, 88, 89}
    group_2 = {5, 6, 7, 8, 9, 26, 27, 28, 29, 47, 48, 49, 50, 68, 69, 70, 71, 90, 91, 92}
    group_3 = {10, 11, 30, 31, 32, 51, 52, 53, 54, 72, 73, 74, 75, 93, 94, 95, 96}
    group_4 = {12, 13, 14, 33, 34, 35, 55, 56, 76, 77, 97, 98}
    group_5 = {15, 16, 36, 37, 57, 58, 78, 79, 80, 99, 100, 101}
    group_6 = {17, 18, 38, 39, 59, 60, 81, 82, 102, 103}
    group_7 = {19, 20, 21, 40, 41, 42, 61, 62, 63, 83, 84, 104, 105}


def process_test_one(answers: list, is_man: bool):
    points_a = points_b = points_c = points_d = points_e = points_f = points_g = points_h = points_i = points_j = 0
    for i, answer in enumerate(answers):
        j = i + 1
        if answer == 1:
            score_position = 0
        elif answer == 0:
            score_position = 1
        elif answer == -1:
            score_position = 2
        if j in TestOneScores.feature_a:
            points_a += TestOneScores.scores[str(j)][score_position]
        elif j in TestOneScores.feature_b:
            points_b += TestOneScores.scores[str(j)][score_position]
        elif j in TestOneScores.feature_c:
            points_c += TestOneScores.scores[str(j)][score_position]
        elif j in TestOneScores.feature_d:
            points_d += TestOneScores.scores[str(j)][score_position]
        elif j in TestOneScores.feature_e:
            points_e += TestOneScores.scores[str(j)][score_position]
        elif j in TestOneScores.feature_f:
            points_f += TestOneScores.scores[str(j)][score_position]
        elif j in TestOneScores.feature_g:
            points_g += TestOneScores.scores[str(j)][score_position]
        elif j in TestOneScores.feature_h:
            points_h += TestOneScores.scores[str(j)][score_position]
        elif j in TestOneScores.feature_i:
            points_i += TestOneScores.scores[str(j)][score_position]
        elif j in TestOneScores.feature_j:
            points_j += TestOneScores.scores[str(j)][score_position]



def process_test_two(data: OrderedDict):
    answers = data['answers']
    is_man = data['is_man']
    correct_answers = getattr(TestTwoAnswers, data['version'])
    result = 0

    for i, value in enumerate(answers):
        j = i + 1
        if value == correct_answers[str(j)]:
            result += 1

    if is_man:
        result += 75
    else:
        result += 70

    return result


def process_test_four(questions: list) -> str:
    results = get_results_for_test_four(questions)
    tests = get_tests_for_test_four(*results)
    return result_for_test_four(*tests)


def get_results_for_test_four(questions: list) -> tuple:
    result_1 = result_2 = result_3 = result_4 = result_5 = result_6 = result_7 = 0

    for i, value in enumerate(questions):
        j = i + 1
        if j in TestFourGroups.group_1:
            if value:
                result_1 += 1
        elif j in TestFourGroups.group_2:
            if value:
                result_2 += 1
        elif j in TestFourGroups.group_3:
            if value:
                result_3 += 1
        elif j in TestFourGroups.group_4:
            if value:
                result_4 += 1
        elif j in TestFourGroups.group_5:
            if value:
                result_5 += 1
        elif j in TestFourGroups.group_6:
            if value:
                result_6 += 1
        elif j in TestFourGroups.group_7:
            if value:
                result_7 += 1

    return result_1, result_2, result_3, result_4, result_5, result_6, result_7


def get_tests_for_test_four(result_1, result_2, result_3, result_4, result_5, result_6, result_7) -> tuple:
    if result_1 > (len(TestFourGroups.group_1) - 1)/2:
        test_1 = True
    else:
        test_1 = False

    if result_2 > len(TestFourGroups.group_2)/2:
        test_2 = True
    else:
        test_2 = False

    if result_3 > len(TestFourGroups.group_3)/2:
        test_3 = True
    else:
        test_3 = False

    if result_4 > (len(TestFourGroups.group_4) - 1)/2:
        test_4 = True
    else:
        test_4 = False

    if result_5 > (len(TestFourGroups.group_5) - 1)/2:
        test_5 = True
    else:
        test_5 = False

    if result_6 > len(TestFourGroups.group_6)/2:
        test_6 = True
    else:
        test_6 = False

    if result_7 > (len(TestFourGroups.group_7) - 1)/2:
        test_7 = True
    else:
        test_7 = False

    return test_1, test_2, test_3, test_4, test_5, test_6, test_7


def result_for_test_four(test_1, test_2, test_3, test_4, test_5, test_6, test_7) -> str:
    if test_1:
        if test_2:
            if test_4:
                return '3.6-4.0'
            else:
                return '3.1-3.5'
        else:
            if test_5:
                return '2.6-3.0'
            else:
                return '2.1-2.5'
    else:
        if test_3:
            if test_6:
                return '1.5-2.0'
            else:
                return '0.1-0.5'
        else:
            if test_7:
                return '0.6-1.0'
            else:
                return '0.1-0.5'
