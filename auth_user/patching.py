import sys

from rest_framework import status
from rest_framework.views import APIView as OriginalAPIView

from auth_user.services import get_user_role
from companies.models import CompanyService


class PatchedAPIView(OriginalAPIView):
    def check_permissions(self, request):
        company_message = self.check_if_company_is_active(request)
        if company_message:
            self.permission_denied(request, message=company_message, code=status.HTTP_403_FORBIDDEN)

        access_service_message = self.check_if_user_has_access_to_service(request)
        if access_service_message:
            self.permission_denied(request, message=access_service_message, code=status.HTTP_403_FORBIDDEN)

        return super().check_permissions(request)

    def check_if_allowed_url(self, request):
        allowed_urls = [
            '/swagger/',
            '/api/auth/token/',
            '/api/tariffs/list-tariff/',
            '/api/app-to-create-company/create/',
            '/api/tests/test-one/',
            '/api/tests/test-two/',
            '/api/tests/test-four/',
        ]
        for url in allowed_urls:
            if request.path.startswith(url):
                return True

        role = get_user_role(request.user)
        if role in ['superuser', 'admin_marketing', 'admin_production_worker']:
            return True

    def check_if_company_is_active(self, request) -> str:
        allowed_url = self.check_if_allowed_url(request)
        if allowed_url:
            return ''
        if not request.user.id:
            return 'Залогиньтесь'

        if not request.user.selected_company.is_active:
            return 'Тариф закончился. Ваша компания не активна'

        return ''

    def check_if_statistic_disabled(self, request, company_services):
        analytics_urls = [
            '/api/tariffs/list-tariff/',
            '/api/user-statistic/',
            '/api/statistic/',
            '/api/stats-for-user/',
            '/api/history-stats-for-user/',
            '/api/create-user-stat/',
            '/api/change-user-stat/',
            '/api/pdf/generate-stat/',
            '/api/pdf/generate-history-stat/'
        ]

        for url in analytics_urls:
            if request.path.startswith(url) and not company_services.analytics_enabled:
                return 'Данный функционал отключен'

    def check_if_time_tracking_disabled(self, request, company_services):
        time_tracking_urls = [
            '/api/timesheet/time-sheet/',
            '/api/timesheet/check-in/',
            '/api/timesheet/check-out/',
            '/api/timesheet/take-time-off/',
            '/api/timesheet/change-timesheet/',
            '/api/timesheet/vacation/',
            '/api/timesheet/last-timesheet/',
        ]
        for url in time_tracking_urls:
            if request.path.startswith(url) and not company_services.time_tracking_enabled:
                return 'Данный функционал отключен'

    def check_if_test_disabled(self, request, company_services):
        tests_urls = [
        ]
        for url in tests_urls:
            if request.path.startswith(url) and not company_services.tests_enabled:
                return 'Данный функционал отключен'

    def check_if_user_has_access_to_service(self, request) -> str:
        allowed_url = self.check_if_allowed_url(request)
        if allowed_url:
            return ''
        try:
            company_services = CompanyService.objects.get(company=request.user.selected_company)
        except CompanyService.DoesNotExist:
            return f'Нужно создать CompanyService для company_id={request.user.selected_company_id}'

        is_statistic_disabled = self.check_if_statistic_disabled(request, company_services)
        if is_statistic_disabled:
            return is_statistic_disabled

        is_time_tracking_disabled = self.check_if_time_tracking_disabled(request, company_services)
        if is_time_tracking_disabled:
            return is_time_tracking_disabled

        is_test_disabled = self.check_if_test_disabled(request, company_services)
        if is_test_disabled:
            return is_test_disabled

        return ''


# We replace the Django REST view with our patched one
sys.modules['rest_framework'].views.APIView = PatchedAPIView
