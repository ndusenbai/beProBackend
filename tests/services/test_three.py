from typing import OrderedDict
from datetime import timedelta


def process_test_three(data: OrderedDict):
    answers = data['answers']
    time = data['time']
    version = data['version']
    points = 0

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

    time_penalty = time.hour*60 + time.minute + time.second*100/60/100
    result = 100 - points - time_penalty
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
