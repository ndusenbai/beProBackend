from typing import OrderedDict


class TestTwo:
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
        '42': 'b',
        '43': 'c',
        '44': 'b',
        '45': 'a',
        '46': 'c',
        '47': 'd',
        '48': 'a',
        '49': 'c',
        '50': 'c',

        '51': 'b',
        '52': 'b',
        '53': 'd',
        '54': 'b',
        '55': 'c',
        '56': 'a',
        '57': 'c',
        '58': 'c',
        '59': 'd',
        '60': 'c',

        '61': 'c',
        '62': 'd',
        '63': 'b',
        '64': 'c',
        '65': 'c',
        '66': 'd',
        '67': 'c',
        '68': 'b',
        '69': 'd',
        '70': 'd',

        '71': 'd',
        '72': 'e',
        '73': 'd',
        '74': 'c',
        '75': 'd',
        '76': 'b',
        '77': 'b',
        '78': 'c',
        '79': 'c',
        '80': 'd',
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
        '23': 'd',
        '24': 'c',
        '25': 'b',
        '26': 'b',
        '27': 'a',
        '28': 'e',
        '29': 'b',
        '30': 'a',

        '31': 'b',
        '32': 'd',
        '33': 'c',
        '34': 'd',
        '35': 'c',
        '36': 'c',
        '37': 'c',
        '38': 'c',
        '39': 'd',
        '40': 'e',

        '41': 'c',
        '42': 'b',
        '43': 'd',
        '44': 'b',
        '45': 'd',
        '46': 'c',
        '47': 'd',
        '48': 'c',
        '49': 'b',
        '50': 'e',

        '51': 'd',
        '52': 'b',
        '53': 'c',
        '54': 'd',
        '55': 'c',
        '56': 'c',
        '57': 'c',
        '58': 'd',
        '59': 'd',
        '60': 'c',

        '61': 'b',
        '62': 'b',
        '63': 'c',
        '64': 'b',
        '65': 'a',
        '66': 'c',
        '67': 'b',
        '68': 'c',
        '69': 'c',
        '70': 'a',

        '71': 'e',
        '72': 'a',
        '73': 'c',
        '74': 'c',
        '75': 'c',
        '76': 'c',
        '77': 'b',
        '78': 'c',
        '79': 'e',
        '80': 'b',
    }

    VERY_HIGH_RESULT = {
        'classification': 'очень высокий',
        'percent': 5,
        'summary': 'старший руководитель – может руководить работниками   напрямую или руководить несколькими руководителями, которые, в свою очередь, непосредственно управляют работниками. Кроме этого, может руководить самой большой или самой важной группой или группами в компании.'
    }
    HIGH_RESULT = {
        'classification': 'высокий',
        'percent': 10,
        'summary': 'старший или младший руководитель– может руководить работниками   напрямую. В основном осуществляет контроль за выполнением производственных заданий. Часто отвечает за непосредственное использование выделенных ему ресурсов.'
    }
    ABOVE_AVERAGE_RESULT = {
        'classification': 'выше среднего',
        'percent': 35,
        'summary': 'не руководящий пост – рекомендуется не давать высокие должности. Не может руководить другими. Но можно поручить менее ответственные задания.'
    }
    BELOW_AVERAGE_RESULT = {
        'classification': 'ниже среднего',
        'percent': 35,
        'summary': 'не руководящий пост, рекомендуется назначать в область, которая хорошо известна и в которой есть опыт работы'
    }
    LOW_RESULT = {
        'classification': 'низкий',
        'percent': 10,
        'summary': 'не руководящий пост, рекомендуется назначать в область, где доказано предварительное обучение или квалификация'
    }
    VERY_LOW_RESULT = {
        'classification': 'очень низкий',
        'percent': 5,
        'summary': 'если не является больным или в некотором отношении неспособным работать, следует поручать только область, в которой доказаны компетентность и квалификация.'
    }

    VERY_HIGH = {
        'min': 135,
        'max': 999,
        'result': VERY_HIGH_RESULT,
    }
    HIGH = {
        'min': 110,
        'max': 134,
        'result': HIGH_RESULT,
    }
    ABOVE_AVERAGE = {
        'min': 100,
        'max': 109,
        'result': ABOVE_AVERAGE_RESULT,
    }
    BELOW_AVERAGE = {
        'min': 90,
        'max': 99,
        'result': BELOW_AVERAGE_RESULT,
    }
    LOW = {
        'min': 80,
        'max': 89,
        'result': LOW_RESULT,
    }
    VERY_LOW = {
        'min': -999,
        'max': 79,
        'result': VERY_LOW_RESULT,
    }


def process_test_two(data: OrderedDict) -> dict:
    points = calculate_points_test_two(data)
    return get_result_test_two(points)


def calculate_points_test_two(data: OrderedDict) -> int:
    answers = data['answers']
    is_man = data['is_man']
    correct_answers = getattr(TestTwo, data['version'])
    points = 0

    for i, value in enumerate(answers):
        j = i + 1
        if value == correct_answers[str(j)]:
            points += 1

    if is_man:
        points += 75
    else:
        points += 70

    return points


def get_result_test_two(points: int) -> dict:
    if TestTwo.VERY_HIGH['min'] <= points <= TestTwo.VERY_HIGH['max']:
        result = TestTwo.VERY_HIGH['result']

    elif TestTwo.HIGH['min'] <= points <= TestTwo.HIGH['max']:
        result = TestTwo.HIGH['result']

    elif TestTwo.ABOVE_AVERAGE['min'] <= points <= TestTwo.ABOVE_AVERAGE['max']:
        result = TestTwo.ABOVE_AVERAGE['result']

    elif TestTwo.BELOW_AVERAGE['min'] <= points <= TestTwo.BELOW_AVERAGE['max']:
        result = TestTwo.BELOW_AVERAGE['result']

    elif TestTwo.LOW['min'] <= points <= TestTwo.LOW['max']:
        result = TestTwo.LOW['result']

    elif TestTwo.VERY_LOW['min'] <= points <= TestTwo.VERY_LOW['max']:
        result = TestTwo.VERY_LOW['result']

    else:
        raise Exception('TestTwo ошибка значений очков')

    result['points'] = points
    return result
