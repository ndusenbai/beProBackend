from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from auth_user import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'assistant', views.AssistantViewSet, basename='assistant-viewset')
router.register(r'observer', views.ObserverViewSet, basename='observer-viewset')
router.register(r'employee-list', views.EmployeeListView, basename='employee-list-view')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', views.ChangePasswordView.as_view({'post': 'change_password'}), name='change-password'),
    path('reset-password/<str:uid>/<str:token>/', views.ForgotPasswordView.as_view(
        {'post': 'new_password', 'get': 'check_link'}), name='new-password'),
    path('reset-password/', views.ForgotPasswordView.as_view({'post': 'reset_password'}), name='reset-password'),
]

urlpatterns += router.urls
