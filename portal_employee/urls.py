from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.EmployeeDashboardView.as_view(), name='employee_dashboard'),
    path('drivers/', views.EmployeeDriverListView.as_view(), name='employee_driver_list'),
    path('drivers/add/', views.EmployeeDriverAddView.as_view(), name='employee_driver_add'),
    path('drivers/<uuid:pk>/edit/', views.EmployeeDriverEditView.as_view(), name='employee_driver_edit'),
    path('drivers/<uuid:pk>/delete/', views.EmployeeDriverDeleteView.as_view(), name='employee_driver_delete'),
    path('drivers/<uuid:pk>/toggle-active/', views.EmployeeDriverToggleView.as_view(), name='employee_driver_toggle'),
    path('drivers/<uuid:pk>/print/', views.EmployeeDriverPrintView.as_view(), name='employee_driver_print'),
]
