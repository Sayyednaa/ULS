from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import home_view, access_denied
from core import views

urlpatterns = [
    path('admin-django/', admin.site.urls),
    
    # Auth
    path('', views.home_view, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html', redirect_authenticated_user=True), name='login'),
    path('register/', views.register_company, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('access-denied/', access_denied, name='access_denied'),
    path('company-status/', views.company_verification_status, name='company_verification_status'),
    path('super-admin/', views.super_admin_dashboard, name='system_admin_dashboard'),
    path('super-admin/stats/', views.system_admin_stats, name='system_admin_stats'),
    path('super-admin/company/<uuid:company_id>/action/', views.super_admin_company_action, name='system_admin_company_action'),

    # Portals
    path('admin-portal/', include('portal_admin.urls')),
    path('manager-portal/', include('portal_manager.urls')),
    path('employee-portal/', include('portal_employee.urls')),
    path('driver-portal/', include('portal_driver.urls')),
    path('accountant-portal/', include('portal_accountant.urls')),

    # Shared
    path('shared/', include('shared.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
