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
QUERY_CODE = openapi.Parameter('code', openapi.IN_QUERY, description='accept code(1000-9999)', type=openapi.TYPE_INTEGER)

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

QUERY_DEPARTMENT = openapi.Parameter('department', openapi.IN_QUERY, description='department id', type=openapi.TYPE_INTEGER)
QUERY_DEPARTMENTS = openapi.Parameter('departments', openapi.IN_QUERY, description='[24,56,...]', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))


QUERY_MONTH = openapi.Parameter('month', openapi.IN_QUERY, description='06', type=openapi.TYPE_INTEGER)
QUERY_YEAR = openapi.Parameter('year', openapi.IN_QUERY, description='2022', type=openapi.TYPE_INTEGER)
QUERY_MONTHS = openapi.Parameter('months', openapi.IN_QUERY, description='[1,2,...,12]', type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
QUERY_ROLE = openapi.Parameter('role_id', openapi.IN_QUERY, description='role id', type=openapi.TYPE_INTEGER)
QUERY_MONDAY = openapi.Parameter('monday', openapi.IN_QUERY, description='monday date (Example: 2022-01-01)', type=openapi.FORMAT_DATE)
QUERY_SUNDAY = openapi.Parameter('sunday', openapi.IN_QUERY, description='sunday date (Example: 2022-01-07)', type=openapi.FORMAT_DATE)
QUERY_STATISTIC_TYPE_LIST = openapi.Parameter('statistic_types', openapi.IN_QUERY, description='GENERAL=1, DOUBLE=2, INVERTED=3',
                                              type=openapi.TYPE_ARRAY,
                                              items=openapi.Items(type=openapi.TYPE_INTEGER),)
