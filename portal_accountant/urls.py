from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.AccountantDashboardView.as_view(), name='accountant_dashboard'),
    path('talabat/', views.AccountantTalabatView.as_view(), name='accountant_talabat'),
    path('pharmazone/', views.AccountantPharmazoneView.as_view(), name='accountant_pharmazone'),
    path('burgerking/', views.AccountantBurgerKingView.as_view(), name='accountant_burgerking'),
    path('other-contract/', views.AccountantOtherContractView.as_view(), name='accountant_other_contract'),
    path('monthly-details/', views.AccountantMonthlyDetailsView.as_view(), name='accountant_monthly_details'),
    
    path('salary-slips/', views.AccountantSalarySlipListView.as_view(), name='accountant_salary_slip_list'),
    path('salary-slips/<uuid:pk>/', views.AccountantSalarySlipView.as_view(), name='accountant_salary_slip'),
    
    path('driver-add/', views.AccountantDriverAddView.as_view(), name='accountant_driver_add'),
    
    path('api/check-pending-deduction/', views.CheckPendingDeductionView.as_view(), name='api_check_pending_deduction'),
    
    # Excel Operations
    path('excel/download-template/<str:model_type>/', views.accountant_download_template, name='accountant_download_template'),
    path('excel/export/<str:model_type>/', views.accountant_export_excel, name='accountant_export_excel'),
    path('excel/upload/<str:model_type>/', views.accountant_upload_excel, name='accountant_upload_excel'),
]
