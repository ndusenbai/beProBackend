from django.urls import path, include


urlpatterns = [
    path('auth/', include('auth_user.api.client.urls'), name='auth'),
]
