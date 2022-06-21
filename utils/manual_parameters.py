from drf_yasg import openapi

QUERY_USER = openapi.Parameter(
    'user_id', openapi.IN_QUERY,
    description='user id',
    type=openapi.TYPE_INTEGER
)
QUERY_STATISTIC_TYPE = openapi.Parameter(
    'statistic_type', openapi.IN_QUERY,
    description='GENERAL=1, DOUBLE=2, INVERTED=3',
    type=openapi.TYPE_INTEGER,
    enum=[1, 2, 3]
)
# applications
QUERY_APPLICATIONS_STATUS = openapi.Parameter(
    'status', openapi.IN_QUERY,
    description='NEW=1, ACCEPTED=2, DECLINED=3',
    type=openapi.TYPE_INTEGER,
    enum=[1, 2, 3]
)
QUERY_EMAIL = openapi.Parameter('email', openapi.IN_QUERY, description='email', type=openapi.TYPE_STRING)

# companies
QUERY_COMPANY = openapi.Parameter('company', openapi.IN_QUERY, description='company id', type=openapi.TYPE_INTEGER)
