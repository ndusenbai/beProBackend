from rest_framework.views import APIView
from .serializers import AppVersionSerializer
from .models import AppVersion
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema


class AppVersionAPI(APIView):

    @swagger_auto_schema(
        responses={200: AppVersionSerializer()}
    )
    def get(self, request):
        app_version = AppVersion.objects.all()
        if app_version.exists():
            serializer = AppVersionSerializer(app_version.first())
            return Response(serializer.data)
        return Response({'message': 'No app versions'}, status=status.HTTP_404_NOT_FOUND)
