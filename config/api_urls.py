from django.urls import path, include


urlpatterns = [
    path('', include('auth_user.urls'), name='auth'),
    path('applications/', include('applications.urls'), name='applications'),
    path('', include('companies.urls'), name='companies'),
    path('scores/', include('scores.urls'), name='scores'),
    path('bepro-stats/', include('bepro_statistics.urls'), name='stats'),
    path('timesheet/', include('timesheet.urls'), name='timesheet'),
    path('tariffs/', include('tariffs.urls'), name='tariffs'),
]

