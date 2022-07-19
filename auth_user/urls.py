from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from auth_user import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('assistant', views.AssistantViewSet, basename='assistant-viewset')
router.register('observer', views.ObserverViewSet, basename='observer-viewset')
router.register('employee-list', views.EmployeeListView, basename='employee-list-view')
router.register('change-company', views.ChangeSelectedCompanyViewSet, basename='change-selected-company')
router.register('owner', views.OwnerViewSet, basename='owner')


urlpatterns = [
    path('auth/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', views.ChangePasswordView.as_view({'post': 'change_password'}), name='change-password'),
    path('auth/reset-password/<str:uid>/<str:token>/', views.ForgotPasswordView.as_view(
        {'post': 'new_password', 'get': 'check_link'}), name='new-password'),
    path('auth/reset-password/', views.ForgotPasswordView.as_view({'post': 'reset_password'}), name='reset-password'),
    path('owner/<int:pk>/activate-owner-companies', views.ActivateOwnerCompaniesViewSet.as_view(), name='activate-owner-companies'),
    path('owner/<int:pk>/deactivate-owner-companies', views.DeactivateOwnerCompaniesViewSet.as_view(), name='deactivate-owner-companies'),
    path('user-profile/', views.UserProfileView.as_view(), name='get-user-profile'),
    path('user-profile/<int:pk>/', views.UpdateUserProfileView.as_view(
        {'patch': 'update'}), name='update-user-profile')

] + router.urls
