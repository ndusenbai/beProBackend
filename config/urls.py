import environ
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from config.admin_urls import urlpatterns as api_admin
from config.client_urls import urlpatterns as api_client


env = environ.Env()
environ.Env.read_env()

schema_view = get_schema_view(
    openapi.Info(
        title="BePro Client API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

admin_schema_view = get_schema_view(
    openapi.Info(
        title="BePro Admin API",
        default_version='',
    ),
    url=env('ADMIN_SCHEME_URL'),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/admin/', include(api_admin)),
    ],
)

client_schema_view = get_schema_view(
    openapi.Info(
        title="BePro Client API",
        default_version='',
    ),
    url=env('CLIENT_SCHEME_URL'),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/client/', include(api_client)),
    ],
)

urlpatterns = [
    path('admin/swagger/', admin_schema_view.with_ui('swagger', cache_timeout=0), name='admin-swagger'),
    path('client/swagger/', client_schema_view.with_ui('swagger', cache_timeout=0), name='client-swagger'),
    path('api/admin/', include('config.admin_urls')),
    path('api/client/', include('config.client_urls')),
    path('admin/', admin.site.urls),
]
