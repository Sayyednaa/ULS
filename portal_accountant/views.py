from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.models import Driver, TalabatSalaryDetail, ContractSalaryDetail, MonthlyProfitLoss
from core.validators import validate_file_extension
from django.core.exceptions import ValidationError

from core.mixins import CompanyDataMixin

class AccountantMixin(LoginRequiredMixin, UserPassesTestMixin, CompanyDataMixin):
    def test_func(self):
        return getattr(self.request.user, 'role', '') in ('accountant', 'superadmin', 'admin')

class AccountantDashboardView(AccountantMixin, TemplateView):
    template_name = 'accountant_portal/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        driver_qs = self.get_queryset_by_company(Driver).filter(is_active=True)
        context['talabat_count'] = driver_qs.filter(contract_type='talabat').count()
        context['pharmazone_count'] = driver_qs.filter(contract_type='pharmazone').count()
        context['burgerking_count'] = driver_qs.filter(contract_type='burger_king').count()
        context['other_count'] = driver_qs.filter(contract_type='other').count()
        context['recent_reports'] = self.get_queryset_by_company(MonthlyProfitLoss).order_by('-created_at')[:5]
        return context

class AccountantTalabatView(AccountantMixin, ListView):
    model = Driver
    template_name = 'accountant_portal/talabat.html'
    context_object_name = 'drivers'

    def get_queryset(self):
        return self.get_queryset_by_company(Driver).filter(is_active=True, contract_type='talabat').order_by('full_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['saved_records'] = self.get_queryset_by_company(TalabatSalaryDetail).select_related('driver').order_by('-created_at')[:50]
        return context

    def post(self, request, *args, **kwargs):
        from decimal import Decimal
        driver_id = request.POST.get('driver_id')
        month_str = request.POST.get('month')  # e.g. "2026-04"
        
        if not driver_id or not month_str:
            messages.error(request, 'Please select a driver and month.')
            return redirect('accountant_talabat')
        
        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            messages.error(request, 'Selected driver not found.')
            return redirect('accountant_talabat')
        
        month_date = f"{month_str}-01"  # convert "2026-04" to "2026-04-01"
        
        def safe_decimal(val):
            if not val or not str(val).strip(): return Decimal('0')
            try: return Decimal(str(val).strip())
            except: return Decimal('0')
            
        def safe_int(val):
            if not val or not str(val).strip(): return 0
            try: return int(float(str(val).strip()))
            except: return 0

        defaults = {
            'batch_1_orders': safe_int(request.POST.get('batch_1_orders')),
            'batch_1_amount': safe_decimal(request.POST.get('batch_1_amount')),
            'batch_1_net_amount': safe_decimal(request.POST.get('batch_1_net_amount')),
            'batch_2_orders': safe_int(request.POST.get('batch_2_orders')),
            'batch_2_amount': safe_decimal(request.POST.get('batch_2_amount')),
            'batch_2_net_amount': safe_decimal(request.POST.get('batch_2_net_amount')),
            'batch_3_orders': safe_int(request.POST.get('batch_3_orders')),
            'batch_3_amount': safe_decimal(request.POST.get('batch_3_amount')),
            'batch_3_net_amount': safe_decimal(request.POST.get('batch_3_net_amount')),
            'batch_4_orders': safe_int(request.POST.get('batch_4_orders')),
            'batch_4_amount': safe_decimal(request.POST.get('batch_4_amount')),
            'batch_4_net_amount': safe_decimal(request.POST.get('batch_4_net_amount')),
            'batch_5_orders': safe_int(request.POST.get('batch_5_orders')),
            'batch_5_amount': safe_decimal(request.POST.get('batch_5_amount')),
            'batch_5_net_amount': safe_decimal(request.POST.get('batch_5_net_amount')),
            'batch_6_orders': safe_int(request.POST.get('batch_6_orders')),
            'batch_6_amount': safe_decimal(request.POST.get('batch_6_amount')),
            'batch_6_net_amount': safe_decimal(request.POST.get('batch_6_net_amount')),
            'batch_7_orders': safe_int(request.POST.get('batch_7_orders')),
            'batch_7_amount': safe_decimal(request.POST.get('batch_7_amount')),
            'batch_7_net_amount': safe_decimal(request.POST.get('batch_7_net_amount')),
            'deduction': safe_decimal(request.POST.get('deduction')),
        }
        
        obj, created = TalabatSalaryDetail.objects.update_or_create(
            driver=driver,
            month=month_date,
            defaults=defaults
        )
        
        # Handle file attachment
        if request.FILES.get('attachment'):
            try:
                validate_file_extension(request.FILES['attachment'])
                obj.attachment = request.FILES['attachment']
                obj.save()
            except ValidationError as e:
                messages.error(request, f"Attachment error: {e.message}")
                
        # Handle signature for salary record
        sig_data = request.POST.get('signature_data')
        sig_image = request.FILES.get('signature_image')
        if sig_data or sig_image:
            if sig_data: obj.signature_data = sig_data
            if sig_image: obj.signature_image = sig_image
            obj.save()
            
        # Handle pending deduction
        installment_id = request.POST.get('installment_id')
        if installment_id:
            from core.models import DeductionInstallment
            from django.utils import timezone
            try:
                inst = DeductionInstallment.objects.get(id=installment_id)
                inst.status = 'paid'
                if not inst.paid_at:
                    inst.paid_at = timezone.now()
                inst.paid_by = request.user
                if sig_data: 
                    inst.signature_data = sig_data
                if sig_image and obj.signature_image: 
                    inst.signature_image = obj.signature_image
                inst.save()
            except DeductionInstallment.DoesNotExist:
                pass
        
        action = 'updated' if not created else 'saved'
        messages.success(request, f'Salary record {action} for {driver.full_name}.')
        return redirect('accountant_talabat')

class AccountantPharmazoneView(AccountantMixin, ListView):
    model = Driver
    template_name = 'accountant_portal/contract_salary.html'
    context_object_name = 'drivers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_title'] = 'Pharma Zone'
        context['contract_type'] = 'pharmazone'
        context['saved_records'] = self.get_queryset_by_company(ContractSalaryDetail).select_related('driver').filter(contract_type='pharmazone').order_by('-created_at')[:50]
        return context

    def get_queryset(self):
        return self.get_queryset_by_company(Driver).filter(is_active=True, contract_type='pharmazone').order_by('full_name')

    def post(self, request, *args, **kwargs):
        return _save_contract_salary(request, 'pharmazone', 'accountant_pharmazone')

class AccountantBurgerKingView(AccountantMixin, ListView):
    model = Driver
    template_name = 'accountant_portal/contract_salary.html'
    context_object_name = 'drivers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_title'] = 'Burger King'
        context['contract_type'] = 'burger_king'
        context['saved_records'] = self.get_queryset_by_company(ContractSalaryDetail).select_related('driver').filter(contract_type='burger_king').order_by('-created_at')[:50]
        return context

    def get_queryset(self):
        return self.get_queryset_by_company(Driver).filter(is_active=True, contract_type='burger_king').order_by('full_name')

    def post(self, request, *args, **kwargs):
        return _save_contract_salary(request, 'burger_king', 'accountant_burgerking')

class AccountantOtherContractView(AccountantMixin, ListView):
    model = Driver
    template_name = 'accountant_portal/contract_salary.html'
    context_object_name = 'drivers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_title'] = 'Other Contracts'
        context['contract_type'] = 'other'
        context['saved_records'] = self.get_queryset_by_company(ContractSalaryDetail).select_related('driver').filter(contract_type='other').order_by('-created_at')[:50]
        return context

    def get_queryset(self):
        return self.get_queryset_by_company(Driver).filter(is_active=True, contract_type='other').order_by('full_name')

    def post(self, request, *args, **kwargs):
        return _save_contract_salary(request, 'other', 'accountant_other_contract')

def _save_contract_salary(request, contract_type, redirect_url):
    from decimal import Decimal
    driver_id = request.POST.get('driver_id')
    month_str = request.POST.get('month')
    
    if not driver_id or not month_str:
        messages.error(request, 'Please select a name and month.')
        return redirect(redirect_url)
    
    try:
        driver = Driver.objects.get(id=driver_id)
    except Driver.DoesNotExist:
        messages.error(request, 'Selected driver not found.')
        return redirect(redirect_url)
    
    name = driver.full_name
    month_date = f"{month_str}-01"
    
    def safe_decimal(val):
        if not val or not str(val).strip(): return Decimal('0')
        try: return Decimal(str(val).strip())
        except: return Decimal('0')
        
    def safe_int(val):
        if not val or not str(val).strip(): return 0
        try: return int(float(str(val).strip()))
        except: return 0

    attachment = request.FILES.get('attachment')
    if attachment:
        try:
            validate_file_extension(attachment)
        except ValidationError as e:
            messages.error(request, f"Attachment error: {e.message}")
            return redirect(redirect_url)

    obj, created = ContractSalaryDetail.objects.update_or_create(
        contract_type=contract_type,
        name=name,
        month=month_date,
        defaults={
            'driver': driver,
            'total_salary': safe_decimal(request.POST.get('total_salary')),
            'absent': safe_int(request.POST.get('absent')),
            'deduction': safe_decimal(request.POST.get('deduction')),
            'remark': request.POST.get('remark', ''),
            'attachment': attachment
        }
    )
    
    sig_data = request.POST.get('signature_data')
    sig_image = request.FILES.get('signature_image')
    if sig_data or sig_image:
        if sig_data: obj.signature_data = sig_data
        if sig_image: obj.signature_image = sig_image
        obj.save()
        
    installment_id = request.POST.get('installment_id')
    if installment_id:
        from core.models import DeductionInstallment
        from django.utils import timezone
        try:
            inst = DeductionInstallment.objects.get(id=installment_id)
            inst.status = 'paid'
            if not inst.paid_at:
                inst.paid_at = timezone.now()
            inst.paid_by = request.user
            if sig_data: 
                inst.signature_data = sig_data
            if sig_image and obj.signature_image: 
                inst.signature_image = obj.signature_image
            inst.save()
        except DeductionInstallment.DoesNotExist:
            pass

    messages.success(request, f'Salary record saved for {name}.')
    return redirect(redirect_url)

from django.http import JsonResponse
from core.models import DeductionInstallment

class CheckPendingDeductionView(AccountantMixin, View):
    def get(self, request):
        driver_id = request.GET.get('driver_id')
        month_str = request.GET.get('month')
        if not driver_id or not month_str:
            return JsonResponse({'amount': 0, 'installment_id': None})
            
        try:
            year, month = map(int, month_str.split('-'))
            from django.db.models import Q
            installments = DeductionInstallment.objects.filter(
                Q(deduction__driver_id=driver_id) | Q(deduction__employee_id=driver_id),
                due_date__year=year,
                due_date__month=month
            )
            if request.user.company:
                installments = installments.filter(deduction__company=request.user.company)
            # Find the first pending installment for this month
            inst = installments.first()
            if inst:
                return JsonResponse({'amount': float(inst.amount), 'installment_id': str(inst.id)})
            return JsonResponse({'amount': 0, 'installment_id': None})
        except Exception as e:
            print("CheckPendingDeductionView Error:", e)
            return JsonResponse({'amount': 0, 'installment_id': None})

class AccountantMonthlyDetailsView(AccountantMixin, ListView):
    model = MonthlyProfitLoss
    template_name = 'accountant_portal/monthly_details.html'
    context_object_name = 'records'
    
    def get_queryset(self):
        return self.get_queryset_by_company(MonthlyProfitLoss).all().order_by('-month')

    def post(self, request, *args, **kwargs):
        company_name = request.POST.get('company_name')
        contract_name = request.POST.get('contract_name')
        expense = request.POST.get('expense')
        profit_loss = request.POST.get('profit_loss')
        month = request.POST.get('month')
        report_pdf = request.FILES.get('report_pdf')

        if company_name and contract_name and expense and profit_loss and month:
            if report_pdf:
                try:
                    validate_file_extension(report_pdf)
                except ValidationError as e:
                    messages.error(request, f"Report PDF error: {e.message}")
                    return redirect('accountant_monthly_details')

            MonthlyProfitLoss.objects.create(
                company_name=company_name,
                contract_name=contract_name,
                expense=expense,
                profit_loss=profit_loss,
                month=month,
                report_pdf=report_pdf
            )
        
        return redirect('accountant_monthly_details')

from core.forms import DriverForm, DeductionForm
from django.contrib import messages

class AccountantDriverAddView(AccountantMixin, View):
    def get(self, request):
        form = DriverForm()
        return render(request, 'admin_portal/driver_form.html', {
            'form': form, 'editing': False, 'portal': 'accountant',
            'title': 'Add New Driver', 'subtitle': 'Register a new driver in the system',
            'breadcrumb': 'Accountant → Drivers → Add', 'icon': '🚗'
        })

    def post(self, request):
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.created_by = request.user
            driver.company = request.user.company
            driver.save()
            messages.success(request, f'Driver {driver.full_name} added successfully.')
            return redirect('accountant_talabat') # Or wherever
        return render(request, 'admin_portal/driver_form.html', {
            'form': form, 'editing': False, 'portal': 'accountant',
            'title': 'Add New Driver', 'subtitle': 'Register a new driver in the system',
            'breadcrumb': 'Accountant → Drivers → Add', 'icon': '🚗'
        })

from django.contrib.auth.decorators import login_required, user_passes_test
from core.excel_utils import generate_excel_template, export_talabat_excel, export_contract_excel, import_from_excel

def is_accountant(user):
    return getattr(user, 'role', '') in ('accountant', 'superadmin', 'admin')

@login_required
@user_passes_test(is_accountant)
def accountant_download_template(request, model_type):
    return generate_excel_template(model_type, request.user)

@login_required
@user_passes_test(is_accountant)
def accountant_export_excel(request, model_type):
    if model_type == 'talabat_salary':
        queryset = TalabatSalaryDetail.objects.filter(company=request.user.company) if request.user.company else TalabatSalaryDetail.objects.all()
        return export_talabat_excel(queryset, label='talabat_salaries')
    elif model_type == 'contract_salary':
        contract_type = request.GET.get('type', '')
        queryset = ContractSalaryDetail.objects.filter(company=request.user.company) if request.user.company else ContractSalaryDetail.objects.all()
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        return export_contract_excel(queryset, label=contract_type or 'all_contracts')
    
    messages.error(request, 'Invalid export type.')
    return redirect('accountant_dashboard')

@login_required
@user_passes_test(is_accountant)
def accountant_upload_excel(request, model_type):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        file = request.FILES['excel_file']
        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Please upload a valid Excel (.xlsx) file.')
        else:
            try:
                validate_file_extension(file)
                count, errors = import_from_excel(file, model_type, request.user)
                if errors:
                    for error in errors[:5]: # Show up to 5 errors
                        messages.error(request, error)
                    if len(errors) > 5:
                        messages.error(request, f"...and {len(errors) - 5} more errors.")
                if count > 0:
                    messages.success(request, f'Successfully imported {count} records.')
                elif not errors:
                    messages.warning(request, 'No records were imported.')
            except ValidationError as e:
                messages.error(request, f"Excel file error: {e.message}")
                
    # redirect back to previous page
    return redirect(request.META.get('HTTP_REFERER', 'accountant_dashboard'))


from core.mixins import FinancialAccessMixin, CompanyDataMixin
class AccountantSalarySlipListView(FinancialAccessMixin, CompanyDataMixin, ListView):
    model = Driver
    template_name = 'accountant_portal/salary_slips.html'
    context_object_name = 'drivers'

    def get_queryset(self):
        qs = self.get_queryset_by_company(Driver).filter(is_active=True)
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(full_name__icontains=q) | qs.filter(working_id__icontains=q) | qs.filter(phone__icontains=q)
        return qs.order_by('full_name')

    def get_context_data(self, **kwargs):
        from datetime import date
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        return context


from django.utils import timezone as tz
from core.models import TalabatSalaryDetail, ContractSalaryDetail

class AccountantSalarySlipView(FinancialAccessMixin, CompanyDataMixin, View):
    """Salary slip that fetches from TalabatSalaryDetail or ContractSalaryDetail,
    matching the data entered on the Talabat / Burger King / Pharmazone salary pages."""

    def get(self, request, pk):
        from datetime import date
        driver = get_object_or_404(Driver, pk=pk)

        # Resolve target month from ?month=YYYY-MM  or fall back to current month
        month_str = request.GET.get('month', '')
        if month_str:
            try:
                target_month = date.fromisoformat(f"{month_str}-01")
            except (ValueError, TypeError):
                target_month = date.today().replace(day=1)
        else:
            target_month = date.today().replace(day=1)

        month_label = target_month.strftime('%B %Y')
        contract_type = driver.contract_type

        salary_record = None
        slip_type = 'talabat'
        batches = []

        if contract_type == 'talabat':
            slip_type = 'talabat'
            salary_record = TalabatSalaryDetail.objects.filter(
                driver=driver, month=target_month
            ).first()
            if salary_record:
                # Build batch rows, skip empty batches
                for i in range(1, 8):
                    orders = getattr(salary_record, f'batch_{i}_orders')
                    amount = getattr(salary_record, f'batch_{i}_amount')
                    net = getattr(salary_record, f'batch_{i}_net_amount')
                    if orders or amount or net:
                        batches.append({
                            'label': f'Batch {i}',
                            'orders': orders,
                            'amount': amount,
                            'net_amount': net,
                        })
        else:
            slip_type = 'contract'
            salary_record = ContractSalaryDetail.objects.filter(
                name__iexact=driver.full_name.strip(),
                contract_type=contract_type,
                month=target_month
            ).first()

        return render(request, 'pdf/accountant_salary_slip.html', {
            'driver': driver,
            'salary_record': salary_record,
            'slip_type': slip_type,
            'batches': batches,
            'month_label': month_label,
            'target_month': target_month,
            'generated_date': tz.now(),
            'contract_type_display': driver.get_contract_type_display(),
        })
