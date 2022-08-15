

class TestFourGroups:
    group_1 = {1, 2, 3, 4, 22, 23, 24, 25, 43, 44, 45, 46, 64, 65, 66, 67, 85, 86, 87, 88, 89}
    group_2 = {5, 6, 7, 8, 9, 26, 27, 28, 29, 47, 48, 49, 50, 68, 69, 70, 71, 90, 91, 92}
    group_3 = {10, 11, 30, 31, 32, 51, 52, 53, 54, 72, 73, 74, 75, 93, 94, 95, 96}
    group_4 = {12, 13, 14, 33, 34, 35, 55, 56, 76, 77, 97, 98}
    group_5 = {15, 16, 36, 37, 57, 58, 78, 79, 80, 99, 100, 101}
    group_6 = {17, 18, 38, 39, 59, 60, 81, 82, 102, 103}
    group_7 = {19, 20, 21, 40, 41, 42, 61, 62, 63, 83, 84, 104, 105}


def process_test_four(questions):
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
