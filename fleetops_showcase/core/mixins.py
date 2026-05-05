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
