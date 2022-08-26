from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin

from tests.exceptions import VersionAlreadyExists
from tests.models import Test
from tests.serializers import TestFourSerializer, TestTwoSerializer, TestOneSerializer, TestThreeSerializer, \
    CreateTestSerializer, TestModelSerializer
from tests.services.test_four import process_test_four
from tests.services.test_one import process_test_one
from tests.services.test_three import process_test_three
from tests.services.test_two import process_test_two
from tests.services.tests import create_test, retrieve_test, submit_test, test_id_encode
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


class TestThreeView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=TestThreeSerializer)
    def post(self, request):
        try:
            serializer = TestThreeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            result = process_test_three(serializer.validated_data)
            return Response({'result': result})
        except Exception as e:
            log_exception(e, 'Error in TestThreeView.post()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestFourView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=TestFourSerializer)
    def post(self, request):
        serializer = TestFourSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_test_four(serializer.validated_data['answers'])
        return Response({'result': result})


class TestViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = (AllowAny,)
    queryset = Test.objects.all()
    serializer_class = TestModelSerializer
    http_method_names = ['get', 'post', 'delete']

    @swagger_auto_schema(request_body=CreateTestSerializer)
    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateTestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            links = create_test(serializer.validated_data)
            return Response(links)
        except VersionAlreadyExists as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except Exception as e:
            log_exception(e, 'Error in TestViewSet.create()')
            return Response({'message': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RetrieveTestViewSet(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response(TestModelSerializer(retrieve_test(kwargs['uid'])).data)


class SubmitTestViewSet(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        submit_test(kwargs['uid'], request.data)
        return Response({'message': 'success'})


# TODO: Delete when not needed
class DecodeIDViewSet(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response({'uid': test_id_encode(kwargs['id'])})
