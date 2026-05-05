from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('drivers/', views.ManagerDriverListView.as_view(), name='manager_driver_list'),
    path('drivers/add/', views.ManagerDriverAddView.as_view(), name='manager_driver_add'),
    path('drivers/<uuid:pk>/edit/', views.ManagerDriverEditView.as_view(), name='manager_driver_edit'),
    path('drivers/<uuid:pk>/delete/', views.ManagerDriverDeleteView.as_view(), name='manager_driver_delete'),
    path('drivers/<uuid:pk>/toggle-active/', views.ManagerDriverToggleView.as_view(), name='manager_driver_toggle'),
    path('drivers/<uuid:pk>/salary-slip/', views.ManagerSalarySlipView.as_view(), name='manager_salary_slip'),
    path('drivers/<uuid:pk>/print/', views.ManagerDriverPrintView.as_view(), name='manager_driver_print'),
]
