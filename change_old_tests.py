import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from tests.models import Test


def update_old_result_for_test_one():
    test_ones = Test.objects.filter(test_type=1, status=2)
    for test_one in test_ones:

        result = test_one.result
        try:
            conclusions = result['conclusions']
            new_conclusions = []
            for conclusion in conclusions:
                    new_conclusions.append(
                        {
                            'ru': conclusion,
                            'kz': conclusion
                        }
                    )
            result['conclusions'] = new_conclusions

            characteristics = result['characteristics']
            new_characteristics = []
            for characteristic in characteristics:
                for category in characteristic:

                    new_characteristics.append(
                        {
                            f'{category}':{
                                            'ru': characteristic[category],
                                            'kz': characteristic[category]
                            }
                        }
                    )

            result['characteristics'] = new_characteristics
            test_one.result = result
            print('+=================================================================')
            print('NEW_RESULT_OF_TEST_ONE_WITH_ID', test_one.id)
            print(result)
            print("END_OF_RESULT_OF_TEST_ONE_WITH_ID", test_one.id)
            print('+=================================================================')
        except KeyError:
            pass


def update_old_result_for_test_two():
    test_twos = Test.objects.filter(test_type=2, status=2)
    for test_two in test_twos:
        result = test_two.result
        try:
            new_result = {
                'kz': {
                    'classification': result['classification'],
                    'percent': result['percent'],
                    'summary': result['summary']
                },
                'points': result['points'],
                'ru': {
                    'classification': result['classification'],
                    'percent': result['percent'],
                    'summary': result['summary']
                }
            }
            test_two.result = new_result
            print('+=================================================================')
            print('NEW_RESULT_OF_TEST_TWO_WITH_ID', test_two.id)
            print(test_two.result)
            print("END_OF_RESULT_OF_TEST_TWO_WITH_ID", test_two.id)
            print('+=================================================================')
        except KeyError:
            pass


def update_old_result_for_test_three():
    test_threes = Test.objects.filter(test_type=3, status=2)
    for test_three in test_threes:
        result = test_three.result
        try:
            new_result = {
                'kz': {
                    'description': result['description']
                },
                'points': result['points'],
                'ru': {
                    'description': result['description']
                }
            }
            test_threes.result = new_result
            print('+=================================================================')
            print('NEW_RESULT_OF_TEST_THREE_WITH_ID', test_three.id)
            print(test_threes.result)
            print("END_OF_RESULT_OF_TEST_THREE_WITH_ID", test_three.id)
            print('+=================================================================')
        except KeyError:
            pass


def update_old_result_for_test_four():
    test_fours = Test.objects.filter(test_type=4, status=2)
    for test_four in test_fours:
        result = test_four.result
        new_characteristics = []
        try:
            for characteristic in result['characteristics']:
                new_characteristics.append(
                    {
                        'kz': {
                            'points': characteristic['points'],
                            'description': characteristic['description'],
                            'characteristic': characteristic['characteristic']
                        },
                        'ru': {
                            'points': characteristic['points'],
                            'description': characteristic['description'],
                            'characteristic': characteristic['characteristic']
                        }
                    }
                )
            result['characteristics'] = new_characteristics
            test_four.result = result
            print('+=================================================================')
            print('NEW_RESULT_OF_TEST_FOUR_WITH_ID', test_four.id)
            print(test_four.result)
            print("END_OF_RESULT_OF_TEST_FOUR_WITH_ID", test_four.id)
            print('+=================================================================')
        except KeyError:
            pass


update_old_result_for_test_one()
update_old_result_for_test_two()
update_old_result_for_test_three()
update_old_result_for_test_four()
