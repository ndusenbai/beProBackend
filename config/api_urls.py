from django.urls import path, include


urlpatterns = [
    path('', include('auth_user.urls'), name='auth'),
    path('', include('applications.urls'), name='applications'),
    path('', include('companies.urls'), name='companies'),
    path('', include('scores.urls'), name='scores'),
    path('', include('bepro_statistics.urls'), name='stats'),
    path('timesheet/', include('timesheet.urls'), name='timesheet'),
    path('tariffs/', include('tariffs.urls'), name='tariffs'),
]

