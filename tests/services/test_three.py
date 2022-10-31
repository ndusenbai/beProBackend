from typing import OrderedDict
from datetime import timedelta

from utils.tools import log_message


class TestThree:
    HIGH = {
        'min': 90,
        'max': 999,
        'result': {'description': 'ВЫСОКИЙ УРОВЕНЬ. Очень хорошая способность к воспроизведению. Такой человек всё понимает и схватывает на лету, и его уровень воспроизведения достаточен для руководителя высшего звена.'}
    }

    GOOD = {
        'min': 80,
        'max': 89,
        'result': {'description': 'ХОРОШИЙ УРОВЕНЬ. Человек с таким воспроизведением хорошо понимает и разбирается в том, что происходит в какой-то определенной области. Такой уровень воспроизведения является достаточным для руководителя высшего или среднего звена.'}
    }

    ACCEPTABLE = {
        'min': 65,
        'max': 79,
        'result': {'description': 'ПРИЕМЛЕМЫЙ УРОВЕНЬ. Человек воспроизводит посредственно, но отнюдь не всегда медленно. Такой уровень достаточен для руководителя низшего звена или для человека, не занимающего руководящую должность.'}
    }

    LOW = {
        'min': -999,
        'max': 64,
        'result': {'description': 'НИЗКИЙ УРОВЕНЬ. Такой человек может быть подвержен несчастным случаям, и ему тяжело приспосабливаться к обстоятельствам. Он может выполнять простые приказы, если он понял, что от него требуется. Человека с таким уровнем воспроизведения не рекомендуется принимать на работу, связанную с управлением каким-либо оборудованием.'}
    }


def process_test_three(data: OrderedDict) -> dict:
    answers = data['answers']
    time = data['time']
    version = data['version']
    points = 0

    log_message(data)

    for i, answer in enumerate(answers):
        if i == 0:
            points = process_question_0(answer, points)
        elif i == 1:
            points = process_question_1(answer, points, version)
        elif i == 2:
            continue
        elif i == 3:
            points = process_question_3(answer, points, version)
        elif i == 4:
            continue
        elif i in [5, 6, 7, 8]:
            points = process_question_5_8(answer, points, version, i)
        elif i == 9:
            points = process_question_9(answer, points, time)
        elif i == 10:
            points = process_question_10(answer, points, version)
        elif i == 11:
            points = process_question_11(answer, points)
        log_message(f'points: {points}, question: {i}')

    time_penalty = (time.hour*60 + time.minute + time.second*100/60/100)*3
    final_points = 100 - points - time_penalty

    log_message(f'calculating points process_test_three')
    log_message(f'time: {time}')
    log_message(f'points: {points}')
    log_message(f'time_penalty: {time_penalty}')
    log_message(f'final_points: {final_points}')

    result = get_result_test_three(final_points)
    return result


def process_question_0(answer: str, points: int) -> int:
    # 'FIRST_NAME LAST_NAME'
    if not answer.isupper():
        points += 10
    return points


def process_question_1(answer: list, points: int, version: str) -> int:
    # ['c', 1]
    answer_option, select = answer
    if select == 2:
        points += 8

    if version == 'A':
        if answer_option == 'a':
            points += 10
        elif answer_option == 'c':
            points += 4

    elif version == 'B':
        if answer_option == 'b':
            points += 4
        elif answer_option == 'c':
            points += 10

    return points


def process_question_3(answer: list, points: int, version: str) -> int:
    # ['a', 2]
    answer_option, select = answer
    if select == 2:  # если использован неправильный символ в селекте
        points += 8

    if version == 'A':
        if answer_option == 'a':
            points += 10
        elif answer_option == 'b':
            points += 4
    elif version == 'B':
        if answer_option == 'a':
            points += 10
        elif answer_option == 'c':
            points += 4

    return points


def process_question_5_8(answer: list, points: int, version: str, i: int) -> int:
    # ['top', '', 'right', '', ,'', 'bottom',]
    correct_answers = None
    if version == 'A':
        if i == 5:
            correct_answers = [1, 4]
        elif i == 6:
            correct_answers = [2, 4]
        elif i == 7:
            correct_answers = [1, 5]
        elif i == 8:
            correct_answers = [3, 5]
    elif version == 'B':
        if i == 5:
            correct_answers = [2, 5]
        elif i == 6:
            correct_answers = [1, 3]
        elif i == 7:
            correct_answers = [2, 4]
        elif i == 8:
            correct_answers = [1, 4]

    right_answers = 0
    picked_answers = 0

    for count, picked in enumerate(answer):
        picked_answers += 1
        if picked != 'top':  # отмечена неправильная сторона
            points += 2
        if count+1 in correct_answers:
            right_answers += 1

    if picked_answers == 0:
        points += 6  # если не выбран ни один ответ
    elif right_answers != 2:
        points += 8  # если ответ неправильный

    return points


def process_question_9(answer: list, points: int, time) -> int:
    # одна галочка на весь вопрос
    # ['a', 'right']
    _answer, position = answer[0], answer[1]
    spent_time = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)

    if position != 'right':  # отмечена неправильная сторона
        points += 2

    if not _answer:  # если нет ответа
        points += 10

    if _answer == 'a':
        points += 10

    if _answer == 'd' and spent_time > timedelta(minutes=5):
        points += 7

    return points


def process_question_10(answer: list, points: int, version: str) -> int:
    # [{"longest": "left", "position": "top"}, {"longest": "left", "position": "top"}, {"longest": "", "position": ""}]
    incorrect_answers_and_points = []
    if version == 'A':
        incorrect_answers_and_points = [('right', 10), ('right', 8), ('left', 8), ('right', 8)]
    elif version == 'B':
        incorrect_answers_and_points = [('right', 10), ('left', 8), ('left', 8), ('left', 8)]

    for i_10, answer_ten in enumerate(answer):
        longest, position = answer_ten['longest'], answer_ten['position']
        if not position:  # если не выбран, неправильно интерпретирован
            points += 10

        if position != 'right':  # если
            points += 2

        if longest == incorrect_answers_and_points[i_10][0]:
            points += incorrect_answers_and_points[i_10][1]

    return points


def process_question_11(answer: list, points: int) -> int:
    left_text, right_text = answer
    first_name = last_name = ''

    if right_text:
        points += 10

    try:
        first_name, last_name = left_text.split()
    except:
        points += 10

    if first_name:
        if not first_name.islower():
            points += 10
    else:
        points += 10
    if last_name:
        if not last_name.isupper():
            points += 10
    else:
        points += 10

    return points


def get_result_test_three(points: int) -> dict:
    if TestThree.HIGH['min'] <= points <= TestThree.HIGH['max']:
        result = TestThree.HIGH['result']

    elif TestThree.GOOD['min'] <= points <= TestThree.GOOD['max']:
        result = TestThree.GOOD['result']

    elif TestThree.ACCEPTABLE['min'] <= points <= TestThree.ACCEPTABLE['max']:
        result = TestThree.ACCEPTABLE['result']

    elif TestThree.LOW['min'] <= points <= TestThree.LOW['max']:
        result = TestThree.LOW['result']

    else:
        raise Exception('TestThree ошибка значений очков')

    result['points'] = points
    return result
