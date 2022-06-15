from django.urls import path, include


urlpatterns = [
    path('auth/', include('auth_user.urls'), name='auth'),
    path('applications/', include('applications.urls'), name='applications'),
    path('companies/', include('companies.urls'), name='companies'),
]
