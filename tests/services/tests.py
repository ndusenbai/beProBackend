from urllib.parse import quote_plus

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

from tests.exceptions import VersionAlreadyExists
from tests.models import Test, TestType
from tests.serializers import TestOneSerializer, TestTwoSerializer, TestThreeSerializer, TestFourSerializer
from tests.services.test_one import process_test_one
from tests.services.test_two import process_test_two
from tests.services.test_three import process_test_three
from tests.services.test_four import process_test_four


def create_test(data):
    force_version = data.pop('force_version')
    if data['version'] and not force_version:
        has_same_test_version = bool(
            Test.objects.filter(
                phone_number=data['phone_number'],
                test_type=data['test_type'],
                version=data['version'])
            .count()
        )
        if has_same_test_version:
            raise VersionAlreadyExists()

    test = Test.objects.create(**data)

    encoded_test_id = urlsafe_base64_encode(force_bytes(test.id))
    link = f'{settings.CURRENT_SITE}/test/?code={encoded_test_id}'
    # link = f'{settings.CURRENT_SITE_WA}/test/?code={encoded_test_id}'
    whatsapp_text = quote_plus(f'Для прохождения теста перейдите по ссылке:\n{link}')
    whatsapp_link = f'https://wa.me/{test.phone_number}?text={whatsapp_text}'
    return {
        'link': link,
        'whatsapp_link': whatsapp_link
    }


def retrieve_test(uid):
    decoded_id = force_str(urlsafe_base64_decode(uid))
    return Test.objects.get(id=decoded_id)


def submit_test(uid, data):
    decoded_id = force_str(urlsafe_base64_decode(uid))
    test = Test.objects.get(id=decoded_id)
    if test.test_type == TestType.ONE_HEART_PRO:
        serializer = TestOneSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        test.result = process_test_one(**serializer.validated_data)
        test.save()
    elif test.test_type == TestType.TWO_BRAIN:
        serializer = TestTwoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        test.result = process_test_two(serializer.validated_data)
        test.save()
    elif test.test_type == TestType.THREE_BRAIN_PRO:
        serializer = TestThreeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        test.result = process_test_three(serializer.validated_data)
        test.save()
    elif test.test_type == TestType.FOUR_HEART:
        serializer = TestFourSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        test.result = process_test_four(serializer.validated_data['answers'])
        test.save()
    else:
        raise Exception('Неправильный тип теста')


def test_id_encode(_id):
    return urlsafe_base64_encode(force_bytes(_id))
