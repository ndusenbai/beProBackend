from django.urls import path, include


urlpatterns = [
    path('', include('auth_user.urls'), name='auth'),
    path('applications/', include('applications.urls'), name='applications'),
    path('companies/', include('companies.urls'), name='companies'),
    path('scores/', include('scores.urls'), name='scores'),
    path('bepro-stats/', include('bepro_statistics.urls'), name='stats')
]

