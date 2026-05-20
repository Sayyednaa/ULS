from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('team/', views.TeamListView.as_view(), name='admin_team_list'),
    path('team/add/', views.TeamAddView.as_view(), name='admin_team_add'),
    path('team/<uuid:pk>/edit/', views.TeamEditView.as_view(), name='admin_team_edit'),
    path('team/<uuid:pk>/delete/', views.TeamDeleteView.as_view(), name='admin_team_delete'),
    path('drivers/', views.DriverListView.as_view(), name='admin_driver_list'),
    path('drivers/add/', views.DriverAddView.as_view(), name='admin_driver_add'),
    path('drivers/<uuid:pk>/edit/', views.DriverEditView.as_view(), name='admin_driver_edit'),
    path('drivers/<uuid:pk>/delete/', views.DriverDeleteView.as_view(), name='admin_driver_delete'),
    path('drivers/<uuid:pk>/toggle-active/', views.DriverToggleActiveView.as_view(), name='admin_driver_toggle'),
    path('drivers/<uuid:pk>/salary-slip/', views.DriverSalarySlipView.as_view(), name='admin_salary_slip'),
    path('drivers/<uuid:pk>/print/', views.DriverProfilePrintView.as_view(), name='admin_driver_print'),
    path('deductions/', views.DeductionListView.as_view(), name='admin_deductions'),
    path('pending-dues/', views.PendingDuesView.as_view(), name='admin_pending_dues'),
    path('pending-dues/<uuid:pk>/pay/', views.MarkInstallmentPaidView.as_view(), name='admin_mark_paid'),
    path('settings/', views.SystemSettingsView.as_view(), name='admin_settings'),
]
