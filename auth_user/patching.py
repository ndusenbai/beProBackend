import sys

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView as OriginalAPIView

from auth_user.services import get_user_role


class PatchedAPIView(OriginalAPIView):
    def check_permissions(self, request):
        message = self.check_is_company_active(request)
        if message:
            self.permission_denied(
                request,
                message=message,
                code=403
            )
        return super().check_permissions(request)

    def check_is_company_active(self, request):
        allowed_urls = [
            '/swagger/',
            '/api/auth/token/',
            '/api/tariffs/list-tariff/',
            '/api/app-to-create-company/create/',
        ]

        role = get_user_role(request.user)

        if role in ['superuser', 'admin_marketing', 'admin_production_worker']:
            return None
        for url in allowed_urls:
            if request.path.startswith(url):
                return None

        if not request.user.id:
            return 'Залогиньтесь'

        if request.user.selected_company.is_active:
            return None

        return 'Тариф закончился. Ваша компания не активна'


# We replace the Django REST view with our patched one
sys.modules['rest_framework'].views.APIView = PatchedAPIView
