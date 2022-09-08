from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('tests/test', views.TestViewSet, basename='test')

urlpatterns = [
    path('tests/<str:uid>/retrieve/', views.RetrieveTestViewSet.as_view(), name='retrieve-test'),
    path('tests/<str:uid>/submit/', views.SubmitTestViewSet.as_view(), name='submit-test'),
    path('tests/<str:uid>/send-email/', views.SendEmailViewSet.as_view(), name='send-email'),
    path('tests/<int:id>/encode/', views.DecodeIDViewSet.as_view(), name='decode-id'),
    path('tests/<int:id>/links/', views.TestLinksView.as_view(), name='test-links'),
    path('tests/<int:company_id>/counters/', views.TestCountersViewSet.as_view(), name='counters'),
] + router.urls
