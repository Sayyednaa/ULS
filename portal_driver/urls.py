from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DriverDashboardView.as_view(), name='driver_dashboard'),
    path('my-profile/', views.DriverMyProfileView.as_view(), name='driver_my_profile'),
]
