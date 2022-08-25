from urllib.parse import quote_plus

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode as ud
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

from tests.exceptions import VersionAlreadyExists
from tests.models import Test


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
    whatsapp_text = quote_plus(f'Для прохождения теста перейдите по ссылке:\n{link}')
    whatsapp_link = f'https://wa.me/{test.phone_number}?text={whatsapp_text}'
    return {
        'link': link,
        'whatsapp_link': whatsapp_link
    }
