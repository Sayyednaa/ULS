from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Base mixin that checks user role against allowed_roles list."""
    allowed_roles = []

    def test_func(self):
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('access_denied')


class SuperAdminRequiredMixin(RoleRequiredMixin):
    """Only superadmin can access."""
    allowed_roles = ['superadmin']


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['superadmin', 'admin']


class AccountantRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['superadmin', 'admin', 'accountant']


class AccountantSuperAdminMixin(RoleRequiredMixin):
    """Only accountant and superadmin can access (deductions, pending dues)."""
    allowed_roles = ['superadmin', 'accountant']


class AdminManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['superadmin', 'admin', 'manager']


class StaffRequiredMixin(RoleRequiredMixin):
    """Access for all office roles including employees."""
    allowed_roles = ['superadmin', 'admin', 'manager', 'employee', 'accountant']


class FinancialAccessMixin(RoleRequiredMixin):
    """Access for admin, manager, and accountant (excludes employee)."""
    allowed_roles = ['superadmin', 'admin', 'manager', 'accountant']


class DriverRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['driver']


class AnyAuthenticatedMixin(LoginRequiredMixin):
    """Any logged-in user can access."""
    pass


class CompanyDataMixin:
    """Mixin to filter querysets by the logged-in user's company."""
    def get_queryset_by_company(self, model_class):
        user = self.request.user
        # If user is a global superuser (Django superuser) and has no company, show everything
        if user.is_superuser and not user.company:
            return model_class.objects.all()
        
        # Otherwise, filter by company. If no company is assigned, return empty to be safe (or all for legacy)
        if user.company:
            return model_class.objects.filter(company=user.company)
        
        # Fallback for existing data/users without companies
        return model_class.objects.all()
