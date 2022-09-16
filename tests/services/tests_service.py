from urllib.parse import quote_plus
from typing import OrderedDict

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.timezone import now
from django.conf import settings
from django.db.transaction import atomic
from django.db.models import F, Sum

from applications.models import TestApplication, TestApplicationStatus
from auth_user.tasks import send_email
from tests.exceptions import VersionAlreadyExists, TestAlreadyFinished, NoEmailTestException, \
    TestAlreadyFinishedEmailException, NoPaidTestException
from tests.models import Test, TestType, TestStatus
from tests.serializers import TestOneSerializer, TestTwoSerializer, TestThreeSerializer, TestFourSerializer
from tests.services.test_one import process_test_one
from tests.services.test_two import process_test_two
from tests.services.test_three import process_test_three
from tests.services.test_four import process_test_four


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


def send_email_invitation(uid):
    decoded_id = force_str(urlsafe_base64_decode(uid))
    test = Test.objects.get(id=decoded_id)
    if not test.email:
        raise NoEmailTestException()
    if test.status != TestStatus.AWAIT:
        raise TestAlreadyFinishedEmailException()

    context = {
        'link': f'{settings.CURRENT_SITE}/test/registration/{uid}/',
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


def generate_test_pdf(test_id: int) -> str:
    # TODO: finish this function
    from django.template.loader import get_template
    from weasyprint import HTML
    from django.utils import timezone
    from django.conf import settings
    import os

    test = Test.objects.get(id=test_id)
    path = 'file://' + os.path.join(settings.BASE_DIR, 'tests', 'static', 'tests')
    context = {
        'test_chart': path + '/test-chart-scale.png',
        'test_human': path + '/test-human.png',
    }
    template = get_template('tests/test_4_html_to_pdf.html')
    html_pdf = template.render(context)
    # return html_pdf
    unique_name = f'test_id_{test_id}_' + timezone.now().strftime("%y-%m-%d-%H-%M-%S")
    pdf_file_name = ''
    match test.test_type:
        case 1:
            pdf_file_name = f'tests_pdf/{unique_name}.pdf'
        case 2:
            pdf_file_name = f'tests_pdf/{unique_name}.pdf'
        case 3:
            pdf_file_name = f'tests_pdf/{unique_name}.pdf'
        case 4:
            pdf_file_name = f'tests_pdf/{unique_name}.pdf'

    HTML(string=html_pdf).write_pdf(settings.MEDIA_ROOT + f"/{pdf_file_name}")
    return f'{settings.CURRENT_SITE}/{pdf_file_name}'
