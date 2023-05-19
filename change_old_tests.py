from tests.models import Test


def update_old_result_for_test_one():
    test_ones = Test.objects.filter(test_type=1, status=2)
    for test_one in test_ones:

        result = test_one.result
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
