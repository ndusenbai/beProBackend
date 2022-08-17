from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from tests.serializers import TestFourSerializer, TestTwoSerializer, TestOneSerializer
from tests.services.test_one import process_test_one
from tests.services.test_two import process_test_two
from tests.services.test_four import process_test_four
from utils.tools import log_exception


class TestOneView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=TestOneSerializer)
    def post(self, request):
        try:
            serializer = TestOneSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            result = process_test_one(**serializer.validated_data)
            return Response({'result': result})
        except Exception as e:
            log_exception(e, 'Error in TestOneView.post()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestTwoView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=TestTwoSerializer)
    def post(self, request):
        serializer = TestTwoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_test_two(serializer.validated_data)
        return Response({'result': result})


class TestFourView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=TestFourSerializer)
    def post(self, request):
        serializer = TestFourSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_test_four(serializer.validated_data['answers'])
        return Response({'result': result})
