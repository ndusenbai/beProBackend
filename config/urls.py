import environ
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

env = environ.Env()
environ.Env.read_env()

schema_view = get_schema_view(
    openapi.Info(
        title="BePro API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    path('api/', include('config.api_urls')),
    path('django-admin/', admin.site.urls),
]
