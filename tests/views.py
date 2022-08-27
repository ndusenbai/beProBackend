from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from tests.exceptions import VersionAlreadyExists
from tests.models import Test
from tests.serializers import CreateTestSerializer, TestModelSerializer
from tests.services.tests import create_test, retrieve_test, submit_test, test_id_encode
from utils.tools import log_exception


class TestViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    # TODO: permission
    permission_classes = (AllowAny,)
    queryset = Test.objects.all()
    serializer_class = TestModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('first_name', 'last_name', 'middle_name', 'created_at')
    filterset_fields = ('company', 'status', 'test_type', 'finished_at')
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
