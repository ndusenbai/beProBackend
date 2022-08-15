from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from tests.serializers import TestFourSerializer
from tests.services import process_test_four


class TestFourView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=TestFourSerializer)
    def post(self, request):
        serializer = TestFourSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_test_four(serializer.validated_data['answers'])
        return Response({'result': result})
