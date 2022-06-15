from drf_yasg import openapi

# applications
QUERY_APPLICATIONS_STATUS = openapi.Parameter('status', openapi.IN_QUERY, description='NEW=1, ACCEPTED=2, DECLINED=3', type=openapi.TYPE_INTEGER, enum=[1, 2, 3])
QUERY_EMAIL = openapi.Parameter('email', openapi.IN_QUERY, description='email', type=openapi.TYPE_STRING)
