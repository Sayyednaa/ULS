"""Employee Portal Views — Read-only driver list, add driver, add deduction, dashboard (no cash)."""
from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from core.mixins import StaffRequiredMixin
from core.models import (
    Profile, Driver, DriverInvoice, Deduction, DeductionInstallment, Notification, Task,
    COMPANY_CHOICES, CONTRACT_CHOICES, VEHICLE_CHOICES,
)
from core.forms import DriverForm, EmployeeDeductionForm, DeductionForm
from portal_admin.views import (
    DriverEditView, DriverDeleteView, DriverToggleActiveView,
    MarkInstallmentPaidView, DriverProfilePrintView
)
from django.views import View


class EmployeeDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        today = date.today()
        month_invoices = DriverInvoice.objects.filter(
            specified_date__year=today.year,
            specified_date__month=today.month,
        )
        totals = month_invoices.aggregate(
            total_orders=Sum('main_orders'),
            total_hours=Sum('hours'),
        )
        total_orders = totals['total_orders'] or 0
        tasks = Task.objects.filter(user=request.user)
        recent_notifs = Notification.objects.filter(user=request.user, is_read=False)[:5]

        return render(request, 'employee_portal/dashboard.html', {
            'total_orders': total_orders,
            'total_hours': totals['total_hours'] or Decimal('0.00'),
            'tasks': tasks,
            'recent_notifs': recent_notifs,
        })


class EmployeeDriverListView(StaffRequiredMixin, View):
    def get(self, request):
        qs = Driver.objects.all()
        q = request.GET.get('q', '')
        company = request.GET.get('company', '')
        contract = request.GET.get('contract', '')
        vehicle = request.GET.get('vehicle', '')

        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(phone__icontains=q))
        if company:
            qs = qs.filter(company_name=company)
        if contract:
            qs = qs.filter(contract_type=contract)
        if vehicle:
            qs = qs.filter(vehicle_type=vehicle)

        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(request.GET.get('page'))

        return render(request, 'admin_portal/driver_list.html', {
            'page_obj': page_obj,
            'q': q,
            'company': company,
            'contract': contract,
            'vehicle': vehicle,
            'company_choices': COMPANY_CHOICES,
            'contract_choices': CONTRACT_CHOICES,
            'vehicle_choices': VEHICLE_CHOICES,
            'portal': 'employee',
        })


class EmployeeDriverAddView(StaffRequiredMixin, View):
    def get(self, request):
        form = DriverForm()
        return render(request, 'admin_portal/driver_form.html', {
            'form': form, 'editing': False, 'portal': 'employee',
            'title': 'Add New Driver', 'subtitle': 'Register a new driver in the system',
            'breadcrumb': 'Employee → Drivers → Add', 'icon': '🚗'
        })

    def post(self, request):
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.created_by = request.user
            driver.save()
            messages.success(request, f'Driver {driver.full_name} added successfully.')
            return redirect('employee_driver_list')
        return render(request, 'admin_portal/driver_form.html', {
            'form': form, 'editing': False, 'portal': 'employee',
            'title': 'Add New Driver', 'subtitle': 'Register a new driver in the system',
            'breadcrumb': 'Employee → Drivers → Add', 'icon': '🚗'
        })


class EmployeeDeductionAddView(StaffRequiredMixin, View):
    def get(self, request):
        form = EmployeeDeductionForm()
        form.fields['driver'].queryset = Driver.objects.filter(is_active=True)
        return render(request, 'employee_portal/deduction_form.html', {
            'form': form,
            'title': 'Submit Deduction', 'subtitle': 'Process a driver deduction record',
            'breadcrumb': 'Employee → Deduction → Add', 'icon': '🧾'
        })

    def post(self, request):
        form = EmployeeDeductionForm(request.POST, request.FILES)
        form.fields['driver'].queryset = Driver.objects.filter(is_active=True)
        if form.is_valid():
            deduction = form.save(commit=False)
            deduction.submitted_by = request.user
            deduction.save()
            messages.success(request, 'Deduction submitted successfully.')
            return redirect('employee_dashboard')
        return render(request, 'employee_portal/deduction_form.html', {
            'form': form,
            'title': 'Submit Deduction', 'subtitle': 'Process a driver deduction record',
            'breadcrumb': 'Employee → Deduction → Add', 'icon': '🧾'
        })

class EmployeeDeductionListView(StaffRequiredMixin, View):
    def get(self, request):
        form = EmployeeDeductionForm()
        form.fields['driver'].queryset = Driver.objects.filter(is_active=True)
        deductions = Deduction.objects.select_related('driver', 'employee', 'submitted_by').all()
        return render(request, 'admin_portal/deduction_invoices.html', {
            'form': form,
            'deductions': deductions,
            'portal': 'employee',
        })

class EmployeePendingDuesView(StaffRequiredMixin, View):
    def get(self, request):
        installments = DeductionInstallment.objects.select_related(
            'deduction__driver', 'deduction__employee'
        ).order_by('status', 'due_date')
        
        q = request.GET.get('q', '')
        if q:
            installments = installments.filter(
                Q(deduction__driver__full_name__icontains=q) |
                Q(deduction__reason__icontains=q)
            )

        return render(request, 'admin_portal/pending_dues.html', {
            'installments': installments,
            'q': q,
            'portal': 'employee',
        })

class EmployeeDriverEditView(DriverEditView):
    pass

class EmployeeDriverDeleteView(DriverDeleteView):
    pass

class EmployeeDriverToggleView(DriverToggleActiveView):
    pass


class EmployeeMarkPaidView(MarkInstallmentPaidView):
    pass

class EmployeeDriverPrintView(DriverProfilePrintView):
    pass
