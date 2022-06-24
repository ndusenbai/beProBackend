from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from auth_user import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'assistant', views.AssistantViewSet, basename='assistant-viewset')
router.register(r'observer', views.ObserverViewSet, basename='observer-viewset')
router.register(r'employee-list', views.EmployeeListView, basename='employee-list-view')
router.register('users', views.UserViewSet, basename='profile')


urlpatterns = [
    path('auth/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', views.ChangePasswordView.as_view({'post': 'change_password'}), name='change-password'),
    path('auth/reset-password/<str:uid>/<str:token>/', views.ForgotPasswordView.as_view(
        {'post': 'new_password', 'get': 'check_link'}), name='new-password'),
    path('auth/reset-password/', views.ForgotPasswordView.as_view({'post': 'reset_password'}), name='reset-password'),
] + router.urls
