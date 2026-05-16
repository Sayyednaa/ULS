"""Admin Portal Views — Full CRUD for team and drivers, dashboard with charts."""
import json
from datetime import date
from decimal import Decimal
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.core.paginator import Paginator
from core.mixins import (
    AdminManagerRequiredMixin, AccountantRequiredMixin,
    FinancialAccessMixin, AccountantSuperAdminMixin,
    SuperAdminRequiredMixin, CompanyDataMixin, StaffRequiredMixin
)
from core.models import (
    Profile, Driver, DriverInvoice, Deduction, DeductionInstallment, Notification, Task,
    SystemSettings,
    ROLE_CHOICES, COMPANY_CHOICES, CONTRACT_CHOICES, VEHICLE_CHOICES,
)
from core.forms import ProfileForm, DriverForm, DeductionForm, DeductionInstallmentForm, TaskAssignmentForm, SystemSettingsForm, CompanyForm
from core.utils import notify_superadmin_action, check_and_notify_expiries
from django.views import View


def get_chart_data(company=None, contract_filter=None, driver_id=None):
    """Compute chart data for dashboard — revenue & orders by vehicle type per month."""
    current_year = date.today().year
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Initialize with zeros
    revenue_bike = [0.0] * 12
    revenue_car = [0.0] * 12
    orders_bike = [0] * 12
    orders_car = [0] * 12

    # One query to get all data for the year
    qs = DriverInvoice.objects.filter(
        specified_date__year=current_year
    )
    
    if company:
        qs = qs.filter(company=company)
        
    if contract_filter:
        # Tie to the contract type stored in the invoice (historical)
        qs = qs.filter(contract_type=contract_filter)
        
    if driver_id:
        qs = qs.filter(driver_id=driver_id)
    
    yearly_data = qs.values(
        'specified_date__month', 'driver__vehicle_type'
    ).annotate(
        total_main=Sum('main_orders'),
    )

    for entry in yearly_data:
        m = entry['specified_date__month'] - 1
        vtype = entry['driver__vehicle_type']
        orders = entry['total_main'] or 0
        
        if vtype == 'bike':
            orders_bike[m] = orders
        else:
            orders_car[m] = orders

    return json.dumps({
        'labels': labels,
        'revenue_bike': revenue_bike,
        'revenue_car': revenue_car,
        'orders_bike': orders_bike,
        'orders_car': orders_car,
    })


class AdminDashboardView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        check_and_notify_expiries(request.user)
        today = date.today()
        contract_filter = request.GET.get('company', '') # This was 'company' in params but actually meant contract type
        driver_id = request.GET.get('driver_id', '')
        
        invoice_qs = self.get_queryset_by_company(DriverInvoice).filter(
            specified_date__year=today.year,
            specified_date__month=today.month,
        )
        driver_qs = self.get_queryset_by_company(Driver).filter(is_active=True)
        
        if contract_filter:
            # Use the contract_type field for historical data integrity
            invoice_qs = invoice_qs.filter(contract_type=contract_filter)
            driver_qs = driver_qs.filter(contract_type=contract_filter)
        
        if driver_id:
            invoice_qs = invoice_qs.filter(driver_id=driver_id)
            driver_qs = driver_qs.filter(id=driver_id)
        
        totals = invoice_qs.aggregate(
            total_orders=Sum('main_orders'),
            total_hours=Sum('hours'),
        )
        total_orders = totals['total_orders'] or 0

        tasks = self.get_queryset_by_company(Task).filter(user=request.user)
        recent_notifs = self.get_queryset_by_company(Notification).filter(user=request.user, is_read=False)[:5]

        expiring_count = 0
        for d in driver_qs:
            if d.has_expiry_warning():
                expiring_count += 1

        return render(request, 'admin_portal/dashboard.html', {
            'total_orders': total_orders,
            'total_hours': totals['total_hours'] or Decimal('0.00'),
            'chart_data': get_chart_data(
                company=request.user.company, 
                contract_filter=contract_filter or None, 
                driver_id=driver_id or None
            ),
            'companies': [c[0] for c in COMPANY_CHOICES],
            'drivers': self.get_queryset_by_company(Driver).filter(
                is_active=True,
                **({'contract_type': contract_filter} if contract_filter else {})
            ).order_by('full_name'),
            'selected_company': contract_filter,
            'selected_driver': driver_id,
            'tasks': tasks,
            'recent_notifs': recent_notifs,
            'active_drivers': driver_qs.count(),
            'expiring_docs': expiring_count,
            'task_assign_form': TaskAssignmentForm(),
            'contract_choices': CONTRACT_CHOICES,
        })


class TeamListView(AdminManagerRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        qs = self.get_queryset_by_company(Profile)
        q = request.GET.get('q', '')
        if q:
            qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))

        sort = request.GET.get('sort', 'first_name')
        direction = request.GET.get('dir', 'asc')
        order_prefix = '' if direction == 'asc' else '-'
        if sort in ['first_name', 'role', 'email']:
            qs = qs.order_by(f'{order_prefix}{sort}')

        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(request.GET.get('page'))

        team_tasks = self.get_queryset_by_company(Task).exclude(user__role='driver').select_related('user', 'assigned_by')

        # Detect portal if not explicitly provided (admin or manager)
        portal_type = 'admin' if request.user.role in ['admin', 'superadmin'] else 'manager'

        return render(request, 'admin_portal/team_list.html', {
            'page_obj': page_obj,
            'team_tasks': team_tasks,
            'q': q,
            'sort': sort,
            'dir': direction,
            'portal': portal_type,
        })


class TeamAddView(AdminManagerRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        form = ProfileForm(user=request.user)
        return render(request, 'admin_portal/team_form.html', {'form': form, 'editing': False})

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Extra safety check for role escalation
            assigned_role = form.cleaned_data.get('role')
            if request.user.role == 'manager' and assigned_role not in ['employee', 'accountant']:
                messages.error(request, "Managers can only add Accountants or Employees.")
                return render(request, 'admin_portal/team_form.html', {'form': form, 'editing': False})
            
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.company = request.user.company # Ensure company is linked
            p1 = form.cleaned_data.get('password1')
            if p1:
                user.set_password(p1)
            user.save()
            
            if request.user.role == 'superadmin':
                notify_superadmin_action(request.user, "Team Member Created", f"created a new team member: {user.get_full_name()}")

            messages.success(request, f'Team member {user.get_full_name()} created successfully.')
            return redirect('admin_team_list')
        return render(request, 'admin_portal/team_form.html', {'form': form, 'editing': False})


class TeamEditView(AdminManagerRequiredMixin, CompanyDataMixin, View):
    def get(self, request, pk):
        member = get_object_or_404(self.get_queryset_by_company(Profile), pk=pk)
        
        # Security: Check hierarchy
        if member.role == 'superadmin' and request.user.role != 'superadmin':
            messages.error(request, "Only Superadmins can modify Superadmin accounts.")
            return redirect('admin_team_list')
        if request.user.role == 'manager' and member.role not in ['employee', 'accountant']:
            messages.error(request, "Managers can only modify Accountants or Employees.")
            return redirect('admin_team_list')

        form = ProfileForm(instance=member, user=request.user)
        return render(request, 'admin_portal/team_form.html', {'form': form, 'editing': True, 'member': member})

    def post(self, request, pk):
        member = get_object_or_404(self.get_queryset_by_company(Profile), pk=pk)
        
        # Security: Check hierarchy
        if member.role == 'superadmin' and request.user.role != 'superadmin':
            messages.error(request, "Only Superadmins can modify Superadmin accounts.")
            return redirect('admin_team_list')
        if request.user.role == 'manager' and member.role not in ['employee', 'accountant']:
            messages.error(request, "Managers can only modify Accountants or Employees.")
            return redirect('admin_team_list')

        form = ProfileForm(request.POST, request.FILES, instance=member, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            p1 = form.cleaned_data.get('password1')
            if p1:
                user.set_password(p1)
            user.save()
            
            if request.user.role == 'superadmin':
                notify_superadmin_action(request.user, "Team Member Updated", f"updated team member: {user.get_full_name()}")

            messages.success(request, f'Team member {user.get_full_name()} updated.')
            return redirect('admin_team_list')
        return render(request, 'admin_portal/team_form.html', {'form': form, 'editing': True, 'member': member})


class TeamDeleteView(AdminManagerRequiredMixin, CompanyDataMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(self.get_queryset_by_company(Profile), pk=pk)
        
        # Security: Check hierarchy
        if member.role == 'superadmin':
            messages.error(request, "Superadmin accounts cannot be deleted through the portal.")
            return redirect('admin_team_list')
            
        if request.user.role == 'manager' and member.role not in ['employee', 'accountant']:
            messages.error(request, "Managers can only delete Accountants or Employees.")
            return redirect('admin_team_list')

        name = member.get_full_name()
        member.delete()

        if request.user.role == 'superadmin':
            notify_superadmin_action(request.user, "Team Member Deleted", f"deleted team member: {name}")

        messages.success(request, f'Team member {name} deleted.')
        return redirect('admin_team_list')


class DriverListView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        qs = self.get_queryset_by_company(Driver)
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
            'portal': 'admin',
        })


class DriverAddView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        form = DriverForm()
        return render(request, 'admin_portal/driver_form.html', {'form': form, 'editing': False})

    def post(self, request):
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.created_by = request.user
            driver.company = request.user.company # Ensure company is linked
            driver.save()
            
            if request.user.role == 'superadmin':
                notify_superadmin_action(request.user, "Driver Created", f"added a new driver: {driver.full_name}", related_driver=driver)

            messages.success(request, f'Driver {driver.full_name} added successfully.')
            return redirect('admin_driver_list')
        return render(request, 'admin_portal/driver_form.html', {'form': form, 'editing': False})


class DriverEditView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request, pk):
        driver = get_object_or_404(self.get_queryset_by_company(Driver), pk=pk)
        form = DriverForm(instance=driver)
        return render(request, 'admin_portal/driver_form.html', {'form': form, 'editing': True, 'driver': driver})

    def post(self, request, pk):
        driver = get_object_or_404(self.get_queryset_by_company(Driver), pk=pk)
        form = DriverForm(request.POST, request.FILES, instance=driver)
        if form.is_valid():
            form.save()
            
            if request.user.role == 'superadmin':
                notify_superadmin_action(request.user, "Driver Updated", f"updated driver info for: {driver.full_name}", related_driver=driver)

            messages.success(request, f'Driver {driver.full_name} updated.')
            return redirect('admin_driver_list')
        return render(request, 'admin_portal/driver_form.html', {'form': form, 'editing': True, 'driver': driver})

class SystemSettingsView(SuperAdminRequiredMixin, View):
    def get(self, request):
        if request.user.company:
            settings_obj = request.user.company
            form = CompanyForm(instance=settings_obj)
            title = 'Company Settings'
            subtitle = 'Manage your company branding and logo'
        else:
            settings_obj = SystemSettings.objects.first()
            if not settings_obj:
                settings_obj = SystemSettings.objects.create(brand_name='UNPREDICTABLE LOGISTICS SOLUTIONS')
            form = SystemSettingsForm(instance=settings_obj)
            title = 'System Settings'
            subtitle = 'Manage global application branding'
        
        return render(request, 'admin_portal/settings.html', {
            'form': form,
            'title': title,
            'subtitle': subtitle,
            'breadcrumb': 'Admin → Settings',
            'icon': '⚙️'
        })

    def post(self, request):
        if request.user.company:
            settings_obj = request.user.company
            form = CompanyForm(request.POST, request.FILES, instance=settings_obj)
        else:
            settings_obj = SystemSettings.objects.first()
            form = SystemSettingsForm(request.POST, request.FILES, instance=settings_obj)
            
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully.')
            return redirect('admin_settings')
        
        title = 'Company Settings' if request.user.company else 'System Settings'
        subtitle = 'Manage your company branding and logo' if request.user.company else 'Manage global application branding'
        
        return render(request, 'admin_portal/settings.html', {
            'form': form,
            'title': title,
            'subtitle': subtitle,
            'breadcrumb': 'Admin → Settings',
            'icon': '⚙️'
        })


class DriverDeleteView(AdminManagerRequiredMixin, View):
    def post(self, request, pk):
        driver = get_object_or_404(Driver, pk=pk)
        name = driver.full_name
        driver.delete()

        if request.user.role == 'superadmin':
            notify_superadmin_action(request.user, "Driver Deleted", f"deleted driver: {name}")

        messages.success(request, f'Driver {name} deleted.')
        return redirect('admin_driver_list')


class DriverToggleActiveView(StaffRequiredMixin, View):
    def post(self, request, pk):
        driver = get_object_or_404(Driver, pk=pk)
        driver.is_active = not driver.is_active
        driver.save()
        status = 'activated' if driver.is_active else 'deactivated'
        messages.success(request, f'Driver {driver.full_name} {status}.')
        return redirect('admin_driver_list')


class DriverSalarySlipView(FinancialAccessMixin, View):
    def get(self, request, pk):
        driver = get_object_or_404(Driver, pk=pk)
        
        # Check for range params first
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        date_str = request.GET.get('date')

        if start_date_str and end_date_str:
            try:
                start_date = date.fromisoformat(start_date_str)
                end_date = date.fromisoformat(end_date_str)
                is_range = True
            except (ValueError, TypeError):
                start_date = end_date = date.today()
                is_range = False
        elif date_str:
            try:
                start_date = end_date = date.fromisoformat(date_str)
                is_range = False
            except (ValueError, TypeError):
                start_date = end_date = date.today()
                is_range = False
        else:
            start_date = end_date = date.today()
            is_range = False

        if is_range:
            invoices = DriverInvoice.objects.filter(driver=driver, specified_date__range=[start_date, end_date])
            totals = invoices.aggregate(
                cash=Sum('cash'),
                main=Sum('main_orders'),
                additional=Sum('additional_orders'),
                hours=Sum('hours')
            )
            invoice = {
                'cash': totals['cash'] or 0,
                'main_orders': totals['main'] or 0,
                'additional_orders': totals['additional'] or 0,
                'hours': totals['hours'] or 0,
                'is_range': True,
                'start_date': start_date,
                'end_date': end_date,
            }
            # Range Deductions
            deductions = Deduction.objects.filter(driver=driver, deduction_date__range=[start_date, end_date])
        else:
            invoice = DriverInvoice.objects.filter(driver=driver, specified_date=start_date).first()
            deductions = Deduction.objects.filter(driver=driver, deduction_date=start_date)

        total_deductions = deductions.aggregate(total=Sum('contractor_deduction_kd'))['total'] or Decimal('0.000')

        return render(request, 'pdf/daily_slip.html', {
            'driver': driver,
            'invoice': invoice,
            'target_date': start_date,
            'start_date': start_date,
            'end_date': end_date,
            'is_range': is_range,
            'deductions': deductions,
            'total_deductions': total_deductions,
            'generated_date': timezone.now(),
        })


class DriverProfilePrintView(StaffRequiredMixin, View):
    def get(self, request, pk):
        driver = get_object_or_404(Driver, pk=pk)
        return render(request, 'pdf/driver_profile.html', {
            'driver': driver,
            'generated_date': timezone.now(),
        })


import json

class DeductionListView(AccountantSuperAdminMixin, CompanyDataMixin, View):
    def get(self, request):
        form = DeductionForm()
        form.fields['driver'].queryset = self.get_queryset_by_company(Driver).filter(is_active=True)
        form.fields['employee'].queryset = self.get_queryset_by_company(Profile).exclude(role='driver')
        
        # Prepare driver data for dynamic filtering in frontend
        active_drivers = self.get_queryset_by_company(Driver).filter(is_active=True).values('id', 'full_name', 'contract_type')
        drivers_json = json.dumps(list(active_drivers), default=str)
        
        deductions = self.get_queryset_by_company(Deduction).select_related('driver', 'employee', 'submitted_by').all()
        return render(request, 'admin_portal/deduction_invoices.html', {
            'form': form,
            'deductions': deductions,
            'drivers_json': drivers_json,
        })

    def post(self, request):
        form = DeductionForm(request.POST, request.FILES)
        form.fields['driver'].queryset = Driver.objects.filter(is_active=True)
        form.fields['employee'].queryset = Profile.objects.exclude(role='driver')
        if form.is_valid():
            deduction = form.save(commit=False)
            deduction.submitted_by = request.user
            deduction.save()

            # Create installments if it's an installment plan
            if deduction.is_installment_plan and deduction.total_installments > 1:
                total_kd = deduction.total_amount
                count = deduction.total_installments
                base_amount = total_kd / count
                
                from datetime import timedelta
                # Simple month increment: approx 30 days
                for i in range(count):
                    # For more accuracy, one could use relativedelta, but let's keep it simple for now
                    # or just increment months manually.
                    due_date = deduction.deduction_date
                    # Logic to increment month
                    month = (due_date.month + i - 1) % 12 + 1
                    year = due_date.year + (due_date.month + i - 1) // 12
                    actual_due_date = date(year, month, min(due_date.day, 28)) # Use 28 to avoid month overflow
                    
                    DeductionInstallment.objects.create(
                        deduction=deduction,
                        amount=base_amount,
                        due_date=actual_due_date,
                        status='pending'
                    )
            elif not deduction.is_installment_plan:
                # Create a single installment for the full amount
                DeductionInstallment.objects.create(
                    deduction=deduction,
                    amount=deduction.total_amount,
                    due_date=deduction.deduction_date,
                    status='pending'
                )

            if request.user.role == 'superadmin':
                target = deduction.driver or deduction.employee
                notify_superadmin_action(request.user, "Deduction Recorded", f"recorded a deduction of {deduction.total_amount} KD for {target}", related_driver=deduction.driver)

            messages.success(request, 'Deduction recorded successfully.')
            return redirect('admin_deductions')
        deductions = Deduction.objects.select_related('driver', 'employee', 'submitted_by').all()
        return render(request, 'admin_portal/deduction_invoices.html', {
            'form': form,
            'deductions': deductions,
        })


class PendingDuesView(AccountantSuperAdminMixin, CompanyDataMixin, View):
    def get(self, request):
        installments = self.get_queryset_by_company(DeductionInstallment).select_related(
            'deduction__driver', 'deduction__employee'
        ).order_by('status', 'due_date')
        
        # Filter logic
        q = request.GET.get('q', '')
        status_filter = request.GET.get('status', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')

        if q:
            installments = installments.filter(
                Q(deduction__driver__full_name__icontains=q) |
                Q(deduction__reason__icontains=q)
            )
        if status_filter:
            installments = installments.filter(status=status_filter)
        if start_date:
            installments = installments.filter(due_date__gte=start_date)
        if end_date:
            installments = installments.filter(due_date__lte=end_date)

        return render(request, 'admin_portal/pending_dues.html', {
            'installments': installments,
            'q': q,
            'status_filter': status_filter,
            'start_date': start_date,
            'end_date': end_date,
            'portal': 'admin',
        })


class MarkInstallmentPaidView(AccountantSuperAdminMixin, CompanyDataMixin, View):
    def post(self, request, pk):
        installment = get_object_or_404(self.get_queryset_by_company(DeductionInstallment), pk=pk)
        
        # Check if marking as paid
        if 'mark_paid' in request.POST:
            installment.status = 'paid'
            installment.paid_at = date.today()
            installment.paid_by = request.user
            
            # Handle signature data (Base64)
            sig_data = request.POST.get('signature_data')
            if sig_data:
                installment.signature_data = sig_data
            
            # Handle signature upload
            if 'signature_image' in request.FILES:
                installment.signature_image = request.FILES['signature_image']
            
            installment.save()
            messages.success(request, f'Installment of {installment.amount} KD marked as paid.')
        
        return redirect('admin_pending_dues')
