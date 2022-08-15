from typing import OrderedDict


class TestFourGroups:
    group_1 = {1, 2, 3, 4, 22, 23, 24, 25, 43, 44, 45, 46, 64, 65, 66, 67, 85, 86, 87, 88, 89}
    group_2 = {5, 6, 7, 8, 9, 26, 27, 28, 29, 47, 48, 49, 50, 68, 69, 70, 71, 90, 91, 92}
    group_3 = {10, 11, 30, 31, 32, 51, 52, 53, 54, 72, 73, 74, 75, 93, 94, 95, 96}
    group_4 = {12, 13, 14, 33, 34, 35, 55, 56, 76, 77, 97, 98}
    group_5 = {15, 16, 36, 37, 57, 58, 78, 79, 80, 99, 100, 101}
    group_6 = {17, 18, 38, 39, 59, 60, 81, 82, 102, 103}
    group_7 = {19, 20, 21, 40, 41, 42, 61, 62, 63, 83, 84, 104, 105}


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


def process_test_two(data: OrderedDict):
    answers = data['answers']
    is_man = data['sex']
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
