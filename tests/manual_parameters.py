from drf_yasg import openapi

QUERY_TEST_STATUS = openapi.Parameter(
    'status', openapi.IN_QUERY,
    description='AWAIT = 1, FINISHED = 2',
    type=openapi.TYPE_INTEGER,
    enum=[1, 2]
)
QUERY_TEST_TYPE = openapi.Parameter(
    'test_type', openapi.IN_QUERY,
    description='ONE_HEART_PRO = 1, TWO_BRAIN = 2, THREE_BRAIN_PRO = 3, FOUR_HEART = 4',
    type=openapi.TYPE_INTEGER,
    enum=[1, 2, 3, 4]
)
QUERY_FINISHED_AT = openapi.Parameter('finished_at', openapi.IN_QUERY, description='date (Example: 2022-01-01)', type=openapi.FORMAT_DATE)
