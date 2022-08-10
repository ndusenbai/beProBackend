import sys

from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView as OriginalAPIView

from auth_user.services import get_user_role


class PatchedAPIView(OriginalAPIView):
    def check_permissions(self, request):
        allowed_urls = [
            '/swagger/',
            '/api/auth/token/',
            '/api/tariffs/list-tariff/',
            '/api/app-to-create-company/create/',
        ]

        role = get_user_role(request.user)

        if role in ['superuser', 'admin_marketing', 'admin_production_worker']:
            return OriginalAPIView.check_permissions(self, request)
        for url in allowed_urls:
            if request.path.startswith(url):
                return OriginalAPIView.check_permissions(self, request)

        if not request.user.id:
            return JsonResponse({'message': 'Залогиньтесь'}, status=status.HTTP_403_FORBIDDEN)

        if request.user.selected_company.is_active:
            return OriginalAPIView.check_permissions(self, request)

        return JsonResponse({'message': 'Тариф закончился. Ваша компания не активна'}, status=status.HTTP_403_FORBIDDEN)


# We replace the Django REST view with our patched one
sys.modules['rest_framework'].views.APIView = PatchedAPIView
