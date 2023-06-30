import os
from typing import OrderedDict
from urllib.parse import quote_plus
from django.contrib.sites.shortcuts import get_current_site

from django.conf import settings
from django.db.models import F, Sum
from django.db.transaction import atomic
from django.template.loader import get_template
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.timezone import now
from weasyprint import HTML

from applications.models import TestApplication, TestApplicationStatus
from auth_user.tasks import send_email
from tests.exceptions import VersionAlreadyExists, TestAlreadyFinished, NoEmailTestException, \
    TestAlreadyFinishedEmailException, NoPaidTestException
from tests.models import Test, TestType, TestStatus
from tests.serializers import TestOneSerializer, TestTwoSerializer, TestThreeSerializer, TestFourSerializer
from tests.services.test_four import process_test_four
from tests.services.test_one import process_test_one
from tests.services.test_three import process_test_three
from tests.services.test_two import process_test_two
from utils.tools import log_message


@atomic
def create_test(data: OrderedDict) -> dict:
    test_app = get_test_application(data)
    check_if_test_version_exists(data)
    test = Test.objects.create(**data)

    if test_app:
        test_app.used_quantity += 1
        if test_app.quantity == test_app.used_quantity:
            test_app.status = TestApplicationStatus.USED
        test_app.save()
    return generate_test_links(test=test)


def get_test_application(data: OrderedDict) -> TestApplication | None:
    if data['test_type'] in Test.PAID_TESTS:
        test_app = TestApplication.objects.filter(
            test_type=data['test_type'],
            company=data['company'],
            status=TestApplicationStatus.ACCEPTED,
            used_quantity__lt=F('quantity'),
        ).order_by('created_at').first()

        if test_app:
            return test_app
        else:
            raise NoPaidTestException()
    else:
        return None


def check_if_test_version_exists(data: OrderedDict):
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


def retrieve_test(uid):
    decoded_id = force_str(urlsafe_base64_decode(uid))
    return Test.objects.get(id=decoded_id)


def submit_test(uid, data):
    decoded_id = force_str(urlsafe_base64_decode(uid))
    test = Test.objects.get(id=decoded_id)

    if test.status == TestStatus.FINISHED:
        raise TestAlreadyFinished()

    if 'hobbies' in data:
        test.hobbies = data['hobbies']
    if 'gender' in data:
        test.gender = data['gender']

    if test.test_type == TestType.ONE_HEART_PRO:
        serializer = TestOneSerializer(data=data['test_data'])
        serializer.is_valid(raise_exception=True)
        result = process_test_one(**serializer.validated_data)
    elif test.test_type == TestType.TWO_BRAIN:
        serializer = TestTwoSerializer(data=data['test_data'])
        serializer.is_valid(raise_exception=True)
        result = process_test_two(serializer.validated_data)
    elif test.test_type == TestType.THREE_BRAIN_PRO:
        log_message(f'Begin process THREE_BRAIN_PRO, id: {test.id}')
        serializer = TestThreeSerializer(data=data['test_data'])
        serializer.is_valid(raise_exception=True)
        result = process_test_three(serializer.validated_data)
    elif test.test_type == TestType.FOUR_HEART:
        serializer = TestFourSerializer(data=data['test_data'])
        serializer.is_valid(raise_exception=True)
        result = process_test_four(serializer.validated_data['answers'])
    else:
        raise Exception('Неправильный тип теста')

    test.result = result
    test.status = TestStatus.FINISHED
    test.finished_at = now().date()
    test.save()


def send_email_invitation(uid, request):
    current_site = get_current_site(request)
    domain_name = current_site.domain
    if 'media.' in domain_name:
        domain_name = domain_name.replace('media.', '')

    protocol = 'https://' if request.is_secure() else 'http://'

    domain = protocol + domain_name

    decoded_id = force_str(urlsafe_base64_decode(uid))
    test = Test.objects.get(id=decoded_id)
    if not test.email:
        raise NoEmailTestException()
    if test.status != TestStatus.AWAIT:
        raise TestAlreadyFinishedEmailException()

    context = {
        'link': f'{settings.CURRENT_SITE}/test/registration/{uid}/',
        'domain': domain
    }
    send_email.delay(subject='Пройдите тест на BePRO.kz', to_list=[test.email], template_name='test_invitation.html', context=context)


def test_id_encode(_id):
    return urlsafe_base64_encode(force_bytes(_id))


def get_counters(company_id: int) -> dict:
    current_tests_1 = Test.objects.filter(
        company_id=company_id,
        test_type=TestType.ONE_HEART_PRO,
        status=TestStatus.AWAIT
    ).count()

    available_tests_1 = TestApplication.objects.filter(
        test_type=TestType.ONE_HEART_PRO,
        company_id=company_id,
        status=TestApplicationStatus.ACCEPTED,
        used_quantity__lt=F('quantity'),
    ).annotate(available_tests=F('quantity')-F('used_quantity')).aggregate(qty=Sum('available_tests'))['qty']
    if available_tests_1 is None:
        available_tests_1 = 0

    current_tests_3 = Test.objects.filter(
        company_id=company_id,
        test_type=TestType.THREE_BRAIN_PRO,
        status=TestStatus.AWAIT
    ).count()

    available_tests_3 = TestApplication.objects.filter(
        test_type=TestType.THREE_BRAIN_PRO,
        company_id=company_id,
        status=TestApplicationStatus.ACCEPTED,
        used_quantity__lt=F('quantity'),
    ).annotate(available_tests=F('quantity')-F('used_quantity')).aggregate(qty=Sum('available_tests'))['qty']
    if available_tests_3 is None:
        available_tests_3 = 0

    return {
        'current_tests_1': current_tests_1,
        'available_tests_1': available_tests_1,
        'current_tests_3': current_tests_3,
        'available_tests_3': available_tests_3,
    }


def generate_test_links(test: Test = None, test_id: int = None) -> dict:
    if test_id is not None:
        test = Test.objects.get(id=test_id)

    uid = urlsafe_base64_encode(force_bytes(test.id))
    link = f'{settings.CURRENT_SITE}/test/registration/{uid}/'
    whatsapp_text = quote_plus(f'Для прохождения теста перейдите по ссылке:\n{link}')
    whatsapp_link = f'https://wa.me/{test.phone_number}?text={whatsapp_text}'
    return {
        'link': link,
        'whatsapp_link': whatsapp_link,
        'uid': uid,
    }


def generate_test_pdf(test_id: int, lang: str) -> str:
    test = Test.objects.get(id=test_id)
    if test.status != TestStatus.FINISHED:
        raise Exception('Нельзя скачать незавершенный тест')

    if test.test_type == TestType.ONE_HEART_PRO:
        return generate_pdf_for_test_one(test, lang)
    elif test.test_type == TestType.TWO_BRAIN:
        return generate_pdf_for_test_two(test, lang)
    elif test.test_type == TestType.THREE_BRAIN_PRO:
        return generate_pdf_for_test_three(test, lang)
    elif test.test_type == TestType.FOUR_HEART:
        return generate_pdf_for_test_four(test, lang)
    else:
        raise Exception('Неверный тип теста')


def generate_pdf_for_test_one(test: Test, lang: str):
    context = get_context_for_pdf_test_one(test, lang)
    template = get_template('tests/test_1_to_pdf.html')
    html_pdf = template.render(context)

    test_name = f'test_id_{test.id}'
    pdf_file_name = f'tests_pdf/tests_one_heart_pro/{test_name}.pdf'

    HTML(string=html_pdf).write_pdf(settings.MEDIA_ROOT + f"/{pdf_file_name}")
    return f'{settings.CURRENT_SITE}/media/{pdf_file_name}'


def get_context_for_pdf_test_one(test: Test, lang: str) -> dict:
    path = 'file://' + os.path.join(settings.BASE_DIR, 'tests', 'static', 'tests')
    height = {}
    color = {}
    characteristics = []
    conclusions = []

    for characteristic_letter, percent_value in test.result['points'].items():
        height[characteristic_letter] = str((percent_value + 100)/2) + '%'
        color[characteristic_letter] = get_color_for_test_one(percent_value)

    for characteristic_dict in test.result['characteristics']:
        for characteristic_title, characteristic_text in characteristic_dict.items():
            if lang in characteristic_text:
                characteristics.append(f'{characteristic_text[lang]}')
            else:
                characteristics.append(f"{characteristic_text}")

    for conclusion in test.result['conclusions']:
        if lang in conclusion:
            conclusions.append(f"{conclusion[lang]['description']}")
        else:
            conclusions.append(f"{conclusion['description']}")

    context = {
        'test_participant': f'{test.first_name} {test.last_name} {test.middle_name}',
        'test_chart': path + '/test-chart-scale.png',
        'test_human': path + '/test-human.png',
        'height': height,
        'color': color,
        'characteristics': characteristics,
        'conclusions': conclusions,
    }
    return context


def get_color_for_test_one(percent):
    if 75 <= percent <= 100:
        return '#0E5001'
    elif 50 <= percent < 75:
        return '#168002'
    elif 25 <= percent < 50:
        return '#20A906'
    elif 0 <= percent < 25:
        return '#4BD730'
    elif -25 <= percent < 0:
        return '#FF7B7B'
    elif -50 <= percent < -25:
        return '#F35858'
    elif -75 <= percent < -50:
        return '#FA2525'
    elif -100 <= percent < -75:
        return '#C70404'

    return 'blue'


def generate_pdf_for_test_two(test: Test, lang: str) -> str:
    context = {
        'test_participant': f'{test.first_name} {test.last_name} {test.middle_name}',
        'points': test.result['points'],
        'classification': test.result['classification'] if lang not in test.result else test.result[lang]['classification'],
        'percent': test.result['percent'] if lang not in test.result else test.result[lang]['percent'],
        'summary': test.result['summary'] if lang not in test.result else test.result[lang]['summary'],
    }
    template = get_template('tests/test_2_to_pdf.html')
    html_pdf = template.render(context)

    test_name = f'test_id_{test.id}'
    pdf_file_name = f'tests_pdf/tests_two_brain/{test_name}.pdf'

    HTML(string=html_pdf).write_pdf(settings.MEDIA_ROOT + f"/{pdf_file_name}")
    return f'{settings.CURRENT_SITE}/media/{pdf_file_name}'


def generate_pdf_for_test_three(test: Test, lang) -> str:
    context = {
        'test_participant': f'{test.first_name} {test.last_name} {test.middle_name}',
        'points': test.result['points'],
        'description': test.result['description'] if lang not in test.result else test.result[lang]['description'],
    }
    template = get_template('tests/test_3_to_pdf.html')
    html_pdf = template.render(context)

    test_name = f'test_id_{test.id}'
    pdf_file_name = f'tests_pdf/tests_three_brain_pro/{test_name}.pdf'

    HTML(string=html_pdf).write_pdf(settings.MEDIA_ROOT + f"/{pdf_file_name}")
    return f'{settings.CURRENT_SITE}/media/{pdf_file_name}'


def generate_pdf_for_test_four(test: Test, lang: str) -> str:
    context = {
        'test_participant': f'{test.first_name} {test.last_name} {test.middle_name}',
        'characteristics': test.result['characteristics'] if lang not in test.result['characteristics'] else test.result[lang]['characteristics'],
    }
    template = get_template('tests/test_4_to_pdf.html')
    html_pdf = template.render(context)

    test_name = f'test_id_{test.id}'
    pdf_file_name = f'tests_pdf/tests_four_heart/{test_name}.pdf'

    HTML(string=html_pdf).write_pdf(settings.MEDIA_ROOT + f"/{pdf_file_name}")
    return f'{settings.CURRENT_SITE}/media/{pdf_file_name}'


def delete_test(test: Test) -> None:
    if test.test_type in Test.FREE_TESTS:
        return

    if test.status == TestStatus.AWAIT:
        test_app = TestApplication.objects.filter(
            test_type=test.test_type,
            company=test.company,
            status=TestApplicationStatus.ACCEPTED,
            used_quantity__lt=F('quantity'),
            used_quantity__gt=0,
        ).order_by('-created_at')

        if test_app:
            test_app = test_app.first()
            test_app.used_quantity -= 1
            test_app.save()
        else:
            test_app = TestApplication.objects.filter(
                test_type=test.test_type,
                company=test.company,
                status=TestApplicationStatus.USED,
            ).order_by('-created_at')

            if test_app:
                test_app = test_app.first()
                test_app.status = TestApplicationStatus.ACCEPTED
                test_app.used_quantity -= 1
                test_app.save()
            else:
                raise Exception('Отсутствуют заявки на тесты')
