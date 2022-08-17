from typing import OrderedDict


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
