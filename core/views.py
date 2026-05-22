from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.db import models
from datetime import datetime, timedelta
from .forms import CompanyRegistrationForm, CompanyVerificationForm
from .models import Company, Profile, Driver

def home_view(request):
    """
    Root URL view: 
    - If logged in, redirect to the appropriate portal.
    - If not logged in, show the landing page.
    """
    if request.user.is_authenticated:
        if request.user.is_superuser and not getattr(request.user, 'company', None):
            return redirect('system_admin_dashboard')
            
        role = getattr(request.user, 'role', None)
        if role in ['admin', 'superadmin']:
            return redirect('admin_dashboard')
        elif role == 'manager':
            return redirect('manager_dashboard')
        elif role == 'employee':
            return redirect('employee_dashboard')
        elif role == 'accountant':
            return redirect('accountant_dashboard')
        elif role == 'driver':
            return redirect('driver_dashboard')
    
    return render(request, 'landing.html')

def access_denied(request):
    return render(request, 'auth/access_denied.html')

def register_company(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create company with logo and currency
                    company = Company.objects.create(
                        name=form.cleaned_data['company_name'],
                        logo=form.cleaned_data['logo'],
                        currency=form.cleaned_data['currency']
                    )
                    
                    # Create superadmin user
                    user = Profile.objects.create_user(
                        username=form.cleaned_data['email'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password1'],
                        company=company,
                        role='superadmin'
                    )
                    
                    # Log the user in
                    login(request, user, backend='core.backends.EmailBackend')
                    return redirect('home')
            except Exception as e:
                form.add_error(None, f"An error occurred: {str(e)}")
    else:
        form = CompanyRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})


@login_required
def company_verification_status(request):
    user = request.user
    if not getattr(user, 'company', None):
        if user.is_superuser:
            return redirect('system_admin_dashboard')
        return redirect('access_denied')
        
    company = user.company
    import datetime
    today = datetime.date.today()
    
    is_expired = False
    if company.status == 'accepted' and company.access_expiry_date:
        if company.access_expiry_date < today:
            is_expired = True
            
    if company.status == 'accepted' and not company.is_paused and not is_expired:
        return redirect('home')
        
    form = None
    if company.status in ['pending_details', 'rejected']:
        if request.method == 'POST':
            form = CompanyVerificationForm(request.POST, request.FILES, instance=company)
            if form.is_valid():
                form.save()
                company.status = 'submitted'
                company.rejection_reason = None
                company.save()
                return redirect('company_verification_status')
        else:
            form = CompanyVerificationForm(instance=company)
            
    return render(request, 'auth/company_status.html', {
        'company': company,
        'form': form,
        'is_expired': is_expired,
        'today': today,
    })


@login_required
def super_admin_dashboard(request):
    if not request.user.is_superuser or getattr(request.user, 'company', None) is not None:
        return redirect('access_denied')
        
    companies = Company.objects.all().order_by('-created_at')
    
    import datetime
    today = datetime.date.today()
    
    total_companies = companies.count()
    pending_count = companies.filter(status='submitted').count()
    review_count = companies.filter(status='under_review').count()
    rejected_count = companies.filter(status='rejected').count()
    paused_count = companies.filter(status='accepted', is_paused=True).count()
    expired_count = companies.filter(status='accepted', access_expiry_date__lt=today).count()
    
    active_count = companies.filter(status='accepted', is_paused=False).filter(
        models.Q(access_expiry_date__gte=today) | models.Q(access_expiry_date__isnull=True)
    ).count()
    
    return render(request, 'admin_portal/super_admin_dashboard.html', {
        'companies': companies,
        'total_companies': total_companies,
        'pending_count': pending_count,
        'review_count': review_count,
        'rejected_count': rejected_count,
        'paused_count': paused_count,
        'expired_count': expired_count,
        'active_count': active_count,
        'today': today,
    })


@login_required
@require_POST
def super_admin_company_action(request, company_id):
    if not request.user.is_superuser or getattr(request.user, 'company', None) is not None:
        return redirect('access_denied')
        
    company = get_object_or_404(Company, id=company_id)
    action = request.POST.get('action')
    
    if action == 'approve':
        company.status = 'accepted'
        company.is_paused = False
        company.access_start_date = timezone.now().date()
        company.access_expiry_date = timezone.now().date() + timedelta(days=7)
        company.save()
        messages.success(request, f"Company '{company.name}' has been approved with 7 days of trial access.")
        
    elif action == 'reject':
        reason = request.POST.get('rejection_reason', '').strip()
        if not reason:
            messages.error(request, "Rejection reason is required.")
        else:
            company.status = 'rejected'
            company.rejection_reason = reason
            company.save()
            messages.success(request, f"Company '{company.name}' has been rejected.")
            
    elif action == 'review':
        company.status = 'under_review'
        company.save()
        messages.success(request, f"Company '{company.name}' is now under review.")
        
    elif action == 'pause':
        company.is_paused = True
        company.save()
        messages.success(request, f"Access for '{company.name}' has been paused.")
        
    elif action == 'resume':
        company.is_paused = False
        company.save()
        messages.success(request, f"Access for '{company.name}' has been resumed.")
        
    elif action == 'extend':
        expiry_date_str = request.POST.get('expiry_date')
        try:
            new_expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            company.access_expiry_date = new_expiry
            company.save()
            messages.success(request, f"Access for '{company.name}' has been set to expire on {new_expiry}.")
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            
    elif action == 'delete':
        profiles = Profile.objects.filter(company=company)
        drivers = Driver.objects.filter(company=company)
        
        from core.models import (
            Deduction, DeductionInstallment, Message, MessageRecipient,
            Notification, Task, CompanyFile, TalabatSalaryDetail,
            ContractSalaryDetail, MonthlyProfitLoss, DriverInvoice, InvoiceArchive,
            DriverReceiving
        )
        
        with transaction.atomic():
            MonthlyProfitLoss.objects.filter(company=company).delete()
            TalabatSalaryDetail.objects.filter(company=company).delete()
            ContractSalaryDetail.objects.filter(company=company).delete()
            
            DeductionInstallment.objects.filter(deduction__company=company).delete()
            DeductionInstallment.objects.filter(paid_by__company=company).delete()
            
            Deduction.objects.filter(company=company).delete()
            Deduction.objects.filter(submitted_by__company=company).delete()
            
            InvoiceArchive.objects.filter(driver__company=company).delete()
            InvoiceArchive.objects.filter(archived_by__company=company).delete()
            
            DriverInvoice.objects.filter(company=company).delete()
            DriverReceiving.objects.filter(company=company).delete()
            CompanyFile.objects.filter(company=company).delete()
            Task.objects.filter(company=company).delete()
            Notification.objects.filter(company=company).delete()
            MessageRecipient.objects.filter(recipient__company=company).delete()
            Message.objects.filter(company=company).delete()
            
            drivers.delete()
            profiles.delete()
            
            company_name = company.name
            company.delete()
            
        messages.success(request, f"Company '{company_name}' and all its associated data have been permanently deleted.")
        
    return redirect('system_admin_dashboard')


@login_required
def system_admin_stats(request):
    if not request.user.is_superuser or getattr(request.user, 'company', None) is not None:
        return redirect('access_denied')

    import os
    import math
    from django.conf import settings
    from core.models import (
        CompanyFile, Deduction, Message, DeductionInstallment,
        InvoiceArchive, DriverInvoice, DriverReceiving, Task
    )

    # Helper function to get file size safely
    def get_file_size(file_field):
        if file_field and hasattr(file_field, 'name') and file_field.name:
            try:
                if os.path.exists(file_field.path):
                    return os.path.getsize(file_field.path)
            except Exception:
                pass
        return 0

    # Helper function to format size in human readable format
    def format_size(size_in_bytes):
        if size_in_bytes <= 0:
            return "0 Bytes"
        units = ["Bytes", "KB", "MB", "GB", "TB"]
        try:
            i = int(math.floor(math.log(size_in_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_in_bytes / p, 2)
            return f"{s} {units[i]}"
        except Exception:
            return f"{size_in_bytes} Bytes"

    # 1. Database Size
    db_size = 0
    try:
        db_engine = settings.DATABASES['default']['ENGINE']
        db_name = settings.DATABASES['default']['NAME']
        
        if 'sqlite' in db_engine:
            if os.path.exists(db_name):
                db_size = os.path.getsize(db_name)
        elif 'postgresql' in db_engine or 'postgis' in db_engine:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_database_size(current_database())")
                row = cursor.fetchone()
                if row:
                    db_size = row[0]
        elif 'mysql' in db_engine:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT SUM(data_length + index_length) FROM information_schema.TABLES WHERE table_schema = %s",
                    [db_name]
                )
                row = cursor.fetchone()
                if row and row[0]:
                    db_size = int(row[0])
    except Exception:
        pass

    # 2. Total record counts
    total_companies = Company.objects.count()
    total_users = Profile.objects.count()
    total_drivers = Driver.objects.count()
    total_deductions = Deduction.objects.count()
    total_messages = Message.objects.count()
    total_tasks = Task.objects.count()
    total_files = CompanyFile.objects.count()
    total_invoices = DriverInvoice.objects.count() + InvoiceArchive.objects.count()

    # 3. Media Directory scan (optional total media files size for system health)
    total_media_size = 0
    media_root = settings.MEDIA_ROOT
    if os.path.exists(media_root):
        for root, dirs, files in os.walk(media_root):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total_media_size += os.path.getsize(fp)
                except Exception:
                    pass

    total_system_storage = db_size + total_media_size

    # 4. Storage occupancy per Company
    companies_data = []
    companies = Company.objects.all()
    for company in companies:
        # Company core documents (logo, certificates, etc.)
        company_docs_size = sum([
            get_file_size(company.logo),
            get_file_size(company.owner_signature),
            get_file_size(company.registration_certificate),
            get_file_size(company.commercial_certificate),
            get_file_size(company.authorized_signature_certificate),
            get_file_size(company.authorized_signature_only),
        ])

        # Company file uploads
        company_files_size = sum(get_file_size(cf.file) for cf in CompanyFile.objects.filter(company=company))

        # Drivers supporting docs and images
        drivers = Driver.objects.filter(company=company)
        drivers_docs_size = 0
        for driver in drivers:
            drivers_docs_size += sum([
                get_file_size(driver.supporting_document),
                get_file_size(driver.civil_id_file),
                get_file_size(driver.driving_license_file),
                get_file_size(driver.work_permit_file),
                get_file_size(driver.health_card_file),
                get_file_size(driver.criminal_pcc_file),
                get_file_size(driver.passport_file),
                get_file_size(driver.vehicle_rc_file),
                get_file_size(driver.photo_selfie),
                get_file_size(driver.other_docs_file),
                get_file_size(driver.received_equipments_file),
            ])

        # Profile/Member files
        profiles = Profile.objects.filter(company=company)
        profile_docs_size = sum(
            get_file_size(p.supporting_document) + get_file_size(p.avatar)
            for p in profiles
        )

        # Deductions proofs and signatures
        deductions_size = sum(get_file_size(d.pdf_proof) for d in Deduction.objects.filter(company=company))
        installments = DeductionInstallment.objects.filter(deduction__company=company)
        signatures_size = sum(get_file_size(i.signature_image) for i in installments)
        deductions_total_size = deductions_size + signatures_size

        # Message attachments
        messages_size = sum(get_file_size(m.attachment) for m in Message.objects.filter(company=company))

        total_company_size = (
            company_docs_size +
            company_files_size +
            drivers_docs_size +
            profile_docs_size +
            deductions_total_size +
            messages_size
        )

        companies_data.append({
            'company': company,
            'company_docs_size': company_docs_size,
            'company_docs_size_formatted': format_size(company_docs_size),
            'company_files_size': company_files_size,
            'company_files_size_formatted': format_size(company_files_size),
            'drivers_docs_size': drivers_docs_size,
            'drivers_docs_size_formatted': format_size(drivers_docs_size),
            'profile_docs_size': profile_docs_size,
            'profile_docs_size_formatted': format_size(profile_docs_size),
            'deductions_size': deductions_total_size,
            'deductions_size_formatted': format_size(deductions_total_size),
            'messages_size': messages_size,
            'messages_size_formatted': format_size(messages_size),
            'total_size': total_company_size,
            'total_size_formatted': format_size(total_company_size),
            'drivers_count': drivers.count(),
            'users_count': profiles.count(),
            'invoices_count': DriverInvoice.objects.filter(company=company).count() + InvoiceArchive.objects.filter(driver__company=company).count(),
        })

    # Sort companies by total storage descending
    companies_data = sorted(companies_data, key=lambda x: x['total_size'], reverse=True)

    # 5. Direct User Storage breakdown (all profiles that have any files)
    users_data = []
    for user in Profile.objects.all():
        avatar_size = get_file_size(user.avatar)
        doc_size = get_file_size(user.supporting_document)
        total_user_size = avatar_size + doc_size
        if total_user_size > 0 or user.is_superuser:  # include superusers or any user with uploaded files
            users_data.append({
                'user': user,
                'avatar_size': avatar_size,
                'avatar_size_formatted': format_size(avatar_size),
                'doc_size': doc_size,
                'doc_size_formatted': format_size(doc_size),
                'total_size': total_user_size,
                'total_size_formatted': format_size(total_user_size),
            })
    users_data = sorted(users_data, key=lambda x: x['total_size'], reverse=True)

    context = {
        'db_size': db_size,
        'db_size_formatted': format_size(db_size),
        'total_media_size': total_media_size,
        'total_media_size_formatted': format_size(total_media_size),
        'total_system_storage': total_system_storage,
        'total_system_storage_formatted': format_size(total_system_storage),
        'total_companies': total_companies,
        'total_users': total_users,
        'total_drivers': total_drivers,
        'total_deductions': total_deductions,
        'total_messages': total_messages,
        'total_tasks': total_tasks,
        'total_files': total_files,
        'total_invoices': total_invoices,
        'companies_data': companies_data,
        'users_data': users_data,
    }
    return render(request, 'admin_portal/super_admin_stats.html', context)



