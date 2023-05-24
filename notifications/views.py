from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .serializers import TestNotificationSerializer
from .services import notify_check_out, notify_check_in
from rest_framework.response import Response
from django.apps import apps
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice


class NotificationHandler(APIView):

    def get(self, request):
        notify_check_out.after_response()
        notify_check_in.after_response()
        return Response({'message': 'OK'})


class TestNotificationAPI(APIView):

    @swagger_auto_schema(request_body=TestNotificationSerializer)
    def post(self, request):
        serializer = TestNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_id = serializer.validated_data['role_id']
        title = serializer.validated_data['title']
        body = serializer.validated_data['body']

        role = apps.get_model(app_label='companies', model_name='Role').objects.filter(id=role_id)
        devices = FCMDevice.objects.filter(user_id=role.user.id)
        devices.send_message(Message(notification=Notification(title=title, body=body)))

        return Response({'message': devices})
