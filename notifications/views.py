from rest_framework.views import APIView

from .services import notify_check_out, notify_check_in
from rest_framework.response import Response



class NotificationHandler(APIView):

    def get(self, request):
        notify_check_out.after_response()
        notify_check_in.after_response()
        return Response({'message': 'OK'})

