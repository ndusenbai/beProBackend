from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from tests.serializers import TestFourSerializer, TestTwoSerializer
from tests.services import process_test_four, process_test_two


class TestFourView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=TestFourSerializer)
    def post(self, request):
        serializer = TestFourSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_test_four(serializer.validated_data['answers'])
        return Response({'result': result})


class TestTwoView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=TestTwoSerializer)
    def post(self, request):
        serializer = TestTwoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_test_two(serializer.validated_data)
        return Response({'result': result})
