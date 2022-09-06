from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from tests.exceptions import VersionAlreadyExists, TestAlreadyFinished, TestAlreadyFinishedEmailException, \
    NoEmailTestException, NoPaidTestException
from tests.models import Test
from tests.serializers import CreateTestSerializer, TestModelSerializer, SubmitTestSerializer, \
    SubmitTestResponseSerializer
from tests.services.tests_service import create_test, retrieve_test, submit_test, test_id_encode, send_email_invitation, \
    get_counters
from utils.permissions import SuperuserOrOwnerOrHRPermission
from utils.tools import log_exception


class TestViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = (SuperuserOrOwnerOrHRPermission,)
    queryset = Test.objects.all()
    serializer_class = TestModelSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('first_name', 'last_name', 'middle_name', 'created_at')
    filterset_fields = ('company', 'status', 'test_type', 'finished_at')
    http_method_names = ['get', 'post', 'delete']

    @swagger_auto_schema(
        request_body=CreateTestSerializer,
        responses={200: SubmitTestResponseSerializer()}
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateTestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            links = create_test(serializer.validated_data)
            return Response(links)
        except VersionAlreadyExists as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except NoPaidTestException as e:
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

    @swagger_auto_schema(request_body=SubmitTestSerializer)
    def post(self, request, *args, **kwargs):
        try:
            serializer = SubmitTestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            submit_test(kwargs['uid'], serializer.validated_data)
            return Response({'message': 'success'})
        except TestAlreadyFinished as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)


class SendEmailViewSet(APIView):
    permission_classes = (SuperuserOrOwnerOrHRPermission,)

    def post(self, request, *args, **kwargs):
        try:
            send_email_invitation(kwargs['uid'])
            return Response({'message': 'success'})
        except NoEmailTestException as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)
        except TestAlreadyFinishedEmailException as e:
            return Response({'message': str(e)}, status.HTTP_423_LOCKED)


# TODO: Delete when not needed
class DecodeIDViewSet(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response({'uid': test_id_encode(kwargs['id'])})


class TestCountersViewSet(APIView):
    permission_classes = (SuperuserOrOwnerOrHRPermission,)

    def get(self, request, *args, **kwargs):
        counters = get_counters(kwargs['company_id'])
        return Response(counters)
