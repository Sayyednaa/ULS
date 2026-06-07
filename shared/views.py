"""Shared Views — Invoices, Archive, Notifications, Messages, Contact, Tasks."""
from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages as django_messages
from django.db.models import Sum, Q
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from core.mixins import AnyAuthenticatedMixin, StaffRequiredMixin, AdminManagerRequiredMixin, FinancialAccessMixin, CompanyDataMixin
from core.models import (
    Driver, DriverInvoice, InvoiceArchive, Notification,
    Message, MessageRecipient, Profile, Task, CompanyFile,
    COMPANY_CHOICES, CONTRACT_CHOICES, DriverReceiving
)
from core.forms import DriverInvoiceForm, MessageForm, TaskForm, CompanyFileForm, ProfileSelfUpdateForm, TaskAssignmentForm, DriverReceivingForm
from core.excel_utils import (
    export_invoices_excel, export_archive_excel, 
    generate_excel_template, import_from_excel
)
from django.views import View


def _parse_month(request):
    """Parse month from query string, default to current month."""
    month_str = request.GET.get('month', '')
    today = date.today()
    if month_str:
        try:
            parts = month_str.split('-')
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            pass
    return today.year, today.month


def _month_label(year, month):
    return date(year, month, 1).strftime('%B %Y')


def _prev_month(year, month):
    d = date(year, month, 1) - timedelta(days=1)
    return f"{d.year}-{d.month:02d}"


def _next_month(year, month):
    if month == 12:
        return f"{year + 1}-01"
    return f"{year}-{month + 1:02d}"


class InvoiceListView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        target_date_str = request.GET.get('date', date.today().isoformat())
        try:
            target_date = date.fromisoformat(target_date_str)
        except ValueError:
            target_date = date.today()

        company_filter = request.GET.get('company', '') # contract type
        driver_id = request.GET.get('driver_id', '')
        drivers = self.get_queryset_by_company(Driver).filter(is_active=True).order_by('full_name')
        if company_filter:
            drivers = drivers.filter(contract_type=company_filter)
        if driver_id:
            drivers = drivers.filter(id=driver_id)
        
        # Prefetch invoices for this date
        invoices = self.get_queryset_by_company(DriverInvoice).filter(specified_date=target_date)
        invoice_map = {inv.driver_id: inv for inv in invoices}
        
        for driver in drivers:
            driver.existing_invoice = invoice_map.get(driver.id)
        
        return render(request, 'shared/driver_invoices.html', {
            'drivers': drivers,
            'all_drivers': self.get_queryset_by_company(Driver).filter(is_active=True).order_by('full_name'),
            'target_date': target_date,
            'target_date_iso': target_date.isoformat(),
            'portal': 'admin' if request.user.role in ('admin', 'superadmin') else ('manager' if request.user.role == 'manager' else 'employee'),
            'contract_choices': CONTRACT_CHOICES,
            'selected_company': company_filter,
            'selected_driver': driver_id,
        })


class InvoiceBulkSaveView(FinancialAccessMixin, View):
    def post(self, request):
        driver_id = request.POST.get('driver_id')
        target_date_str = request.POST.get('date')
        
        def safe_decimal(val):
            if not val or not val.strip(): return Decimal('0')
            try: return Decimal(val.strip())
            except: return Decimal('0')
            
        def safe_int(val):
            if not val or not val.strip(): return 0
            try: return int(float(val.strip()))
            except: return 0

        main_delta = safe_int(request.POST.get('main_orders'))
        additional_delta = safe_int(request.POST.get('additional_orders'))
        cash_delta = safe_decimal(request.POST.get('cash'))
        hours_delta = safe_decimal(request.POST.get('hours'))

        driver = get_object_or_404(self.get_queryset_by_company(Driver), id=driver_id)
        
        with transaction.atomic():
            invoice, created = DriverInvoice.objects.get_or_create(
                driver=driver,
                specified_date=date.fromisoformat(target_date_str),
                defaults={
                    'main_orders': main_delta,
                    'additional_orders': additional_delta,
                    'cash': cash_delta,
                    'hours': hours_delta,
                    'created_by': request.user.profile,
                    'company': request.user.company
                }
            )
            
            if not created:
                invoice.main_orders = main_delta
                invoice.additional_orders = additional_delta
                invoice.cash = cash_delta
                invoice.hours = hours_delta
                invoice.updated_at = timezone.now()
                invoice.save()

        django_messages.success(request, f'Updated totals for {driver.full_name}.')
        return redirect(f'/shared/invoices/?date={target_date_str}')


class InvoiceResetView(StaffRequiredMixin, View):
    def post(self, request):
        driver_id = request.POST.get('driver_id')
        target_date_str = request.POST.get('date')
        all_reset = request.POST.get('all') == 'true'

        if all_reset:
            self.get_queryset_by_company(DriverInvoice).filter(specified_date=target_date_str).update(
                main_orders=0, hours=0
            )
            django_messages.success(request, f'Reset all totals for {target_date_str}.')
        else:
            driver = get_object_or_404(self.get_queryset_by_company(Driver), id=driver_id)
            DriverInvoice.objects.filter(driver=driver, specified_date=target_date_str).update(
                main_orders=0, hours=0
            )
            django_messages.success(request, f'Reset totals for {driver.full_name}.')

        return redirect(f'/shared/invoices/?date={target_date_str}')


class InvoiceAddView(StaffRequiredMixin, View):
    def post(self, request):
        form = DriverInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.company = request.user.company
            invoice.save()
            django_messages.success(request, 'Invoice entry added.')
        else:
            django_messages.error(request, 'Error adding invoice entry. Check form fields.')
        month = request.POST.get('current_month', '')
        return redirect(f'/shared/invoices/?month={month}' if month else '/shared/invoices/')


class InvoiceEditView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request, pk):
        invoice = get_object_or_404(self.get_queryset_by_company(DriverInvoice), pk=pk)
        # Employee can only edit own
        if request.user.role == 'employee' and invoice.created_by != request.user:
            return redirect('access_denied')
        form = DriverInvoiceForm(instance=invoice)
        form.fields['driver'].queryset = self.get_queryset_by_company(Driver).filter(is_active=True)
        return render(request, 'shared/invoice_edit.html', {'form': form, 'invoice': invoice})

    def post(self, request, pk):
        invoice = get_object_or_404(self.get_queryset_by_company(DriverInvoice), pk=pk)
        if request.user.role == 'employee' and invoice.created_by != request.user:
            return redirect('access_denied')
        form = DriverInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Invoice updated.')
            return redirect('/shared/invoices/')
        return render(request, 'shared/invoice_edit.html', {'form': form, 'invoice': invoice})


class InvoiceDeleteView(StaffRequiredMixin, CompanyDataMixin, View):
    def post(self, request, pk):
        invoice = get_object_or_404(self.get_queryset_by_company(DriverInvoice), pk=pk)
        if request.user.role == 'employee' and invoice.created_by != request.user:
            return redirect('access_denied')
        invoice.delete()
        django_messages.success(request, 'Invoice entry deleted.')
        return redirect('/shared/invoices/')


class InvoiceArchiveActionView(StaffRequiredMixin, View):
    def post(self, request):
        month_str = request.POST.get('month', '')
        try:
            parts = month_str.split('-')
            year, month = int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            django_messages.error(request, 'Invalid month.')
            return redirect('/shared/invoices/')

        invoices = self.get_queryset_by_company(DriverInvoice).filter(
            specified_date__year=year, specified_date__month=month,
        )
        if not invoices.exists():
            django_messages.warning(request, 'No invoices to archive for this month.')
            return redirect('/shared/invoices/')

        with transaction.atomic():
            # Aggregate per driver
            drivers_in_month = invoices.values('driver').distinct()
            for d in drivers_in_month:
                driver = Driver.objects.get(pk=d['driver'])
                driver_invoices = invoices.filter(driver=driver)
                totals = driver_invoices.aggregate(
                    cash=Sum('cash'), main=Sum('main_orders'),
                    additional=Sum('additional_orders'), hours=Sum('hours'),
                )
                InvoiceArchive.objects.create(
                    driver=driver,
                    driver_name=driver.full_name,
                    main_orders=totals['main'] or 0,
                    hours=totals['hours'] or 0,
                    archive_date=date(year, month, 1),
                    archived_by=request.user
                )
            invoices.delete()

        django_messages.success(request, f'{_month_label(year, month)} invoices archived successfully.')
        return redirect('/shared/archive/')


class InvoiceExportView(StaffRequiredMixin, View):
    def get(self, request):
        year, month = _parse_month(request)
        qs = self.get_queryset_by_company(DriverInvoice).filter(
            specified_date__year=year, specified_date__month=month,
        ).select_related('driver').order_by('driver__full_name', 'specified_date')
        return export_invoices_excel(qs, f"{year}-{month:02d}")


class ArchiveListView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        qs = self.get_queryset_by_company(InvoiceArchive, company_field='driver__company').select_related('driver').all()
        q = request.GET.get('q', '')
        company = request.GET.get('company', '') # contract type
        contract = request.GET.get('contract', '')
        month_str = request.GET.get('month', '')

        if q:
            qs = qs.filter(driver_name__icontains=q)
        if month_str:
            try:
                parts = month_str.split('-')
                qs = qs.filter(archive_date__year=int(parts[0]), archive_date__month=int(parts[1]))
            except (ValueError, IndexError):
                pass
        if company:
            qs = qs.filter(driver__company_name=company)
        if contract:
            qs = qs.filter(driver__contract_type=contract)

        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(request.GET.get('page'))

        # Fetch drivers for the Add Archive modal
        drivers = self.get_queryset_by_company(Driver).filter(is_active=True).values('id', 'full_name', 'civil_id_number')
        drivers_list = list(drivers)
        for d in drivers_list:
            d['id'] = str(d['id'])
            
        import json

        return render(request, 'shared/archive.html', {
            'page_obj': page_obj,
            'q': q,
            'company': company,
            'contract': contract,
            'month': month_str,
            'company_choices': COMPANY_CHOICES,
            'contract_choices': CONTRACT_CHOICES,
            'drivers_json': json.dumps(drivers_list),
        })


class ArchiveAddView(StaffRequiredMixin, CompanyDataMixin, View):
    def post(self, request):
        import json
        from django.http import JsonResponse
        from core.models import Driver
        
        try:
            data = json.loads(request.body)
        except:
            data = {}
            
        driver_id = data.get('driver_id')
        archive_number = data.get('archive_number', '')
        archive_date = data.get('archive_date')
        
        if not driver_id or not archive_date:
            return JsonResponse({'error': 'Driver and Archive Date are required'}, status=400)
            
        try:
            driver = self.get_queryset_by_company(Driver).get(id=driver_id)
        except Driver.DoesNotExist:
            return JsonResponse({'error': 'Driver not found'}, status=404)
            
        InvoiceArchive.objects.create(
            driver=driver,
            driver_name=driver.full_name,
            archive_number=archive_number,
            archive_date=archive_date,
            cash=0,
            main_orders=0,
            additional_orders=0,
            hours=0,
            archived_by=request.user
        )
        
        return JsonResponse({'success': True})

class ArchiveEditView(AdminManagerRequiredMixin, CompanyDataMixin, View):
    def post(self, request, pk):
        import json
        from django.http import JsonResponse
        from core.models import Driver
        try:
            data = json.loads(request.body)
        except:
            data = {}
            
        archive_number = data.get('archive_number', '')
        archive_date = data.get('archive_date')
        
        if not archive_date:
            return JsonResponse({'error': 'Archive Date is required'}, status=400)
            
        try:
            archive = self.get_queryset_by_company(InvoiceArchive, company_field='driver__company').get(id=pk)
            archive.archive_number = archive_number
            archive.archive_date = archive_date
            archive.save()
            return JsonResponse({'success': True})
        except InvoiceArchive.DoesNotExist:
            return JsonResponse({'error': 'Archive not found'}, status=404)

class ArchiveDeleteView(AdminManagerRequiredMixin, CompanyDataMixin, View):
    def post(self, request, pk):
        from django.http import JsonResponse
        try:
            archive = self.get_queryset_by_company(InvoiceArchive, company_field='driver__company').get(id=pk)
            archive.delete()
            return JsonResponse({'success': True})
        except InvoiceArchive.DoesNotExist:
            return JsonResponse({'error': 'Archive not found'}, status=404)

class ArchiveExportView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        qs = self.get_queryset_by_company(InvoiceArchive, company_field='driver__company').all()
        return export_archive_excel(qs, 'all')


class NotificationListView(AnyAuthenticatedMixin, CompanyDataMixin, View):
    def get(self, request):
        notifications = self.get_queryset_by_company(Notification).filter(user=request.user)
        return render(request, 'shared/notifications.html', {'notifications': notifications})


class NotificationReadView(AnyAuthenticatedMixin, CompanyDataMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(self.get_queryset_by_company(Notification), pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return redirect('/shared/notifications/')


class NotificationReadAllView(AnyAuthenticatedMixin, CompanyDataMixin, View):
    def post(self, request):
        self.get_queryset_by_company(Notification).filter(user=request.user, is_read=False).update(is_read=True)
        django_messages.success(request, 'All notifications marked as read.')
        return redirect('/shared/notifications/')


class NotificationClearAllView(AnyAuthenticatedMixin, CompanyDataMixin, View):
    def post(self, request):
        self.get_queryset_by_company(Notification).filter(user=request.user).delete()
        django_messages.success(request, 'Notification history cleared.')
        return redirect('/shared/notifications/')


class MessageInboxView(AnyAuthenticatedMixin, View):
    def get(self, request):
        inbox = MessageRecipient.objects.filter(
            recipient=request.user
        ).select_related('message', 'message__sender').order_by('-message__created_at')
        sent = Message.objects.filter(sender=request.user).order_by('-created_at')
        return render(request, 'shared/messages_inbox.html', {
            'inbox': inbox,
            'sent': sent,
        })


class MessageDetailView(AnyAuthenticatedMixin, View):
    def get(self, request, pk):
        msg = get_object_or_404(Message, pk=pk)
        # Mark as read if recipient
        mr = MessageRecipient.objects.filter(message=msg, recipient=request.user).first()
        
        # Security Check: User must be sender or recipient
        if msg.sender != request.user and not mr:
            return redirect('access_denied')

        if mr and not mr.is_read:
            mr.is_read = True
            mr.read_at = timezone.now()
            mr.save()
        return render(request, 'shared/message_detail.html', {'msg': msg, 'mr': mr})


class MessageReadView(AnyAuthenticatedMixin, View):
    def post(self, request, pk):
        mr = get_object_or_404(MessageRecipient, message_id=pk, recipient=request.user)
        mr.is_read = True
        mr.read_at = timezone.now()
        mr.save()
        return redirect('/shared/messages/')


class MessageComposeView(StaffRequiredMixin, View):
    def get(self, request):
        pre_recipient_id = request.GET.get('to')
        initial = {}
        if pre_recipient_id:
            try:
                # Still filter by company for security
                qs = Profile.objects.filter(company=request.user.company) if request.user.company else Profile.objects.all()
                initial['recipient'] = qs.get(pk=pre_recipient_id)
            except (Profile.DoesNotExist, ValueError):
                pass
        
        form = MessageForm(initial=initial)
        return render(request, 'shared/messages_compose.html', {
            'form': form,
        })

    def post(self, request):
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.save()
            
            recipient = form.cleaned_data['recipient']
            MessageRecipient.objects.create(message=msg, recipient=recipient)
            
            django_messages.success(request, 'Message sent successfully.')
            return redirect('/shared/messages/')
        return render(request, 'shared/messages_compose.html', {'form': form})


class ContactView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        qs = self.get_queryset_by_company(Profile).all()
        q = request.GET.get('q', '')
        if q:
            qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))
        return render(request, 'shared/contact.html', {'team': qs, 'q': q})


class TaskAddView(AnyAuthenticatedMixin, View):
    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.company = request.user.company
            task.save()
            django_messages.success(request, 'Task added.')
        redirect_url = request.META.get('HTTP_REFERER', '/')
        return redirect(redirect_url)


class TaskAssignView(AdminManagerRequiredMixin, View):
    def post(self, request):
        form = TaskAssignmentForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.company = request.user.company
            task.save()
            django_messages.success(request, f'Task assigned to {task.user.get_full_name()}.')
        else:
            django_messages.error(request, 'Error assigning task.')
        return redirect(request.META.get('HTTP_REFERER', '/'))


class TaskToggleView(AnyAuthenticatedMixin, View):
    def post(self, request, pk):
        # Allow user to toggle their own tasks
        task = get_object_or_404(Task, pk=pk, user=request.user)
        if task.status == 'pending':
            task.status = 'completed'
            task.completed_at = timezone.now()
        else:
            task.status = 'pending'
            task.completed_at = None
        task.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))


class TaskDeleteView(AnyAuthenticatedMixin, View):
    def post(self, request, pk):
        # ONLY allow deleting if the user created it (self-task) or is manager/admin
        task = get_object_or_404(Task, pk=pk, user=request.user)
        
        # If it was assigned by someone else, employee cannot delete it
        if task.assigned_by and task.assigned_by != request.user and request.user.role == 'employee':
            django_messages.error(request, "You cannot delete tasks assigned by others.")
        else:
            task.delete()
            django_messages.success(request, "Task removed.")
            
        return redirect(request.META.get('HTTP_REFERER', '/'))


# ─── Company Files Archive ───────────────────────────────────────────────────

class CompanyFileListView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        qs = self.get_queryset_by_company(CompanyFile).all()
        q = request.GET.get('q', '')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(category__icontains=q))
        
        form = CompanyFileForm()
        return render(request, 'shared/company_files.html', {
            'files': qs,
            'q': q,
            'form': form
        })

    def post(self, request):
        form = CompanyFileForm(request.POST, request.FILES)
        if form.is_valid():
            cfile = form.save(commit=False)
            cfile.uploaded_by = request.user.profile if hasattr(request.user, 'profile') else None
            cfile.company = request.user.company
            cfile.save()
            django_messages.success(request, 'Company file uploaded successfully.')
        return redirect('company_files')


class CompanyFileUpdateView(StaffRequiredMixin, View):
    def post(self, request, pk):
        cfile = get_object_or_404(CompanyFile, pk=pk)
        form = CompanyFileForm(request.POST, request.FILES, instance=cfile)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Company file updated.')
        return redirect('company_files')


class CompanyFileDeleteView(AdminManagerRequiredMixin, View):
    def post(self, request, pk):
        cfile = get_object_or_404(CompanyFile, pk=pk)
        cfile.delete()
        django_messages.success(request, 'Company file deleted.')
        return redirect('company_files')


# ─── Deactivated Drivers ────────────────────────────────────────────────────

class DeactivatedDriversView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        drivers = self.get_queryset_by_company(Driver).filter(is_active=False).order_by('full_name')
        return render(request, 'shared/deactivated_drivers.html', {'drivers': drivers})


# ─── Bulk Upload & Templates ────────────────────────────────────────────────

class TemplateDownloadView(StaffRequiredMixin, View):
    def get(self, request, model_type):
        return generate_excel_template(model_type, request.user)


class BulkUploadView(StaffRequiredMixin, View):
    def post(self, request, model_type):
        file = request.FILES.get('excel_file')
        if not file:
            django_messages.error(request, 'No file uploaded.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        try:
            from core.validators import validate_file_extension
            validate_file_extension(file)
            
            count, errors = import_from_excel(file, model_type, request.user)
            if count > 0:
                django_messages.success(request, f'Successfully imported {count} records.')
            if errors:
                for err in errors:
                    django_messages.error(request, err)
        except Exception as e:
            django_messages.error(request, f"Upload error: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/'))
class ProfileView(AnyAuthenticatedMixin, View):
    def get(self, request):
        form = ProfileSelfUpdateForm(instance=request.user)
        return render(request, 'shared/profile.html', {'form': form})

    def post(self, request):
        form = ProfileSelfUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        return render(request, 'shared/profile.html', {'form': form})

class DriverReceivingsView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        qs = self.get_queryset_by_company(DriverReceiving).select_related('driver').all()
        q = request.GET.get('q', '')
        if q:
            qs = qs.filter(Q(driver__full_name__icontains=q) | Q(custom_label__icontains=q))
            
        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(request.GET.get('page'))

        form = DriverReceivingForm()
        # Only active drivers
        form.fields['driver'].queryset = self.get_queryset_by_company(Driver).filter(is_active=True).order_by('full_name')

        return render(request, 'shared/driver_receivings.html', {
            'page_obj': page_obj,
            'q': q,
            'form': form,
        })

    def post(self, request):
        form = DriverReceivingForm(request.POST, request.FILES)
        # Apply queryset filtering for driver to avoid cross-company additions
        form.fields['driver'].queryset = self.get_queryset_by_company(Driver).filter(is_active=True)

        if form.is_valid():
            receiving = form.save(commit=False)
            receiving.company = request.user.company
            receiving.save()
            django_messages.success(request, f'Receiving added for {receiving.driver.full_name}.')
            return redirect('driver_receivings')

        # Error case
        qs = self.get_queryset_by_company(DriverReceiving).select_related('driver').all()
        paginator = Paginator(qs, 20)
        page_obj = paginator.get_page(request.GET.get('page'))
        return render(request, 'shared/driver_receivings.html', {
            'page_obj': page_obj,
            'q': request.GET.get('q', ''),
            'form': form,
        })

class DriverReceivingsDeleteView(StaffRequiredMixin, CompanyDataMixin, View):
    def post(self, request, pk):
        receiving = get_object_or_404(self.get_queryset_by_company(DriverReceiving), pk=pk)
        name = receiving.get_item_name()
        driver_name = receiving.driver.full_name
        receiving.delete()
        django_messages.success(request, f'Deleted {name} receiving for {driver_name}.')
        return redirect('driver_receivings')

class OperationDocumentsView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        drivers = self.get_queryset_by_company(Driver).filter(is_active=True).order_by('full_name')
        
        drivers_data = []
        for d in drivers:
            company_display = dict(COMPANY_CHOICES).get(d.company_name, d.company_name) if d.company_name else ''
            drivers_data.append({
                'id': str(d.id),
                'full_name': d.full_name,
                'company_name': company_display,
                'civil_id': d.civil_id_number,
                'designation': d.position or 'Car Driver',
                'vehicle_name': d.vehicle_name,
                'vehicle_plate_number': d.vehicle_plate_number,
                'phone': d.phone,
            })
            
        from core.models import OperationDocumentHistory
        history_records = self.get_queryset_by_company(OperationDocumentHistory).order_by('-created_at')[:20]
        
        initial_data = None
        history_id = request.GET.get('history_id')
        if history_id:
            try:
                record = self.get_queryset_by_company(OperationDocumentHistory).get(id=history_id)
                initial_data = record.content_data
            except OperationDocumentHistory.DoesNotExist:
                pass
        
        import json
        return render(request, 'shared/operation_documents.html', {
            'drivers_json': json.dumps(drivers_data),
            'drivers': drivers,
            'history_records': history_records,
            'initial_data_json': json.dumps(initial_data) if initial_data else 'null',
            'viewing_history': bool(initial_data)
        })


class SaveOperationDocumentView(StaffRequiredMixin, CompanyDataMixin, View):
    def post(self, request):
        import json
        from django.http import JsonResponse
        from core.models import Driver, OperationDocumentHistory
        
        try:
            data = json.loads(request.body)
            driver_id = data.get('driver_id')
            doc_type = data.get('doc_type') or data.get('docType')
            due_date = data.get('due_date') or data.get('dueDate')
            
            if not driver_id or not doc_type:
                return JsonResponse({'error': 'Missing driver or document type'}, status=400)
                
            driver = self.get_queryset_by_company(Driver).get(id=driver_id)
            
            # Format due date if provided
            parsed_due_date = None
            if due_date:
                try:
                    from datetime import datetime
                    parsed_due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            # Save history
            history_record = OperationDocumentHistory.objects.create(
                creator=request.user,
                driver=driver,
                doc_type=doc_type,
                due_date=parsed_due_date,
                content_data=data,
                company=driver.company
            )
            
            # Auto-create Deduction if penalty_deduction
            if doc_type == 'penalty_deduction':
                from core.models import Deduction, DeductionInstallment
                from datetime import date
                deduction_amount = float(data.get('deduction_amount', 0) or 0)
                if deduction_amount > 0:
                    doc_date_str = data.get('doc_date')
                    try:
                        from datetime import datetime
                        doc_date = datetime.strptime(doc_date_str, '%Y-%m-%d').date() if doc_date_str else datetime.now().date()
                    except:
                        doc_date = date.today()
                        
                    is_installment = bool(data.get('is_installment', False))
                    total_installments = int(data.get('total_installments', 1) or 1) if is_installment else 1
                    reason = data.get('violation_reason', 'Administrative Penalty Deduction')
                    
                    deduction = Deduction.objects.create(
                        driver=driver,
                        employee=None,
                        reason=reason,
                        deduction_date=doc_date,
                        contracting_company=driver.contract_type or 'other',
                        contractor_deduction_kd=0,
                        company_deduction_kd=deduction_amount,
                        is_installment_plan=is_installment,
                        total_installments=total_installments,
                        traffic_violation=False,
                        company=driver.company,
                        submitted_by=request.user
                    )
                    
                    if is_installment and total_installments > 1:
                        base_amount = deduction_amount / total_installments
                        for i in range(total_installments):
                            month = (doc_date.month + i - 1) % 12 + 1
                            year = doc_date.year + (doc_date.month + i - 1) // 12
                            actual_due_date = date(year, month, min(doc_date.day, 28))
                            
                            DeductionInstallment.objects.create(
                                deduction=deduction,
                                amount=base_amount,
                                due_date=actual_due_date,
                                status='pending'
                            )
            
            return JsonResponse({'success': True, 'history_id': str(history_record.id)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class PrintOperationDocumentView(StaffRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        history_id = request.GET.get('history_id')
        if not history_id:
            return redirect('operation_documents')
            
        from core.models import OperationDocumentHistory, Driver, COMPANY_CHOICES
        try:
            record = self.get_queryset_by_company(OperationDocumentHistory).get(id=history_id)
        except OperationDocumentHistory.DoesNotExist:
            return redirect('operation_documents')
            
        import json
        
        from django.utils import timezone
        from core.models import SystemSettings
        
        driver = None
        if record.driver:
            driver = record.driver
            
        data = record.content_data or {}
        
        # Helper to convert English digits to Arabic digits
        def to_arabic_digits(text):
            if not text:
                return ''
            text = str(text)
            arabic_digits = {'0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤', '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'}
            for eng, ar in arabic_digits.items():
                text = text.replace(eng, ar)
            return text
            
        # Format dates for templates
        date_en = record.created_at.strftime('%Y-%m-%d')
        date_ar = to_arabic_digits(date_en)
        date_month_en = record.created_at.strftime('%B %Y')
        date_month_ar = to_arabic_digits(date_month_en)
        
        system_settings = SystemSettings.objects.first()
        company_name = system_settings.brand_name if system_settings else data.get('company_name', '')
        company_name_ar = data.get('company_name_ar', '')
        
        company_logo_url = None
        if record.company and record.company.logo:
            company_logo_url = record.company.logo.url
        elif system_settings and system_settings.logo:
            company_logo_url = system_settings.logo.url
        
        context = {
            'record': record,
            'driver': driver,
            'data': data,
            'auto_print': request.GET.get('print', 'true') == 'true',
            'date_en': data.get('formatted_date') or date_en,
            'date_ar': data.get('formatted_date_ar') or date_ar,
            'date_month_en': data.get('formatted_date_month') or date_month_en,
            'date_month_ar': data.get('formatted_date_month_ar') or date_month_ar,
            'company_name': company_name,
            'company_name_ar': data.get('company_name_ar') or company_name_ar,
            'company_logo_url': company_logo_url,
            'driver_name_ar': data.get('driver_name_ar', ''),
            'civil_id_ar': to_arabic_digits(data.get('civil_id_number_ar', driver.civil_id_number if driver else '')),
            'deduction_amount_ar': to_arabic_digits(data.get('deduction_amount', '00.00')),
            'inst1_amount_ar': to_arabic_digits(data.get('inst1_amount', '00.00')),
            'inst2_amount_ar': to_arabic_digits(data.get('inst2_amount', '00.00')),
            'inst3_amount_ar': to_arabic_digits(data.get('inst3_amount', '00.00')),
            'inst4_amount_ar': to_arabic_digits(data.get('inst4_amount', '00.00')),
            'serial_number_ar': to_arabic_digits(data.get('serial_number', '')),
            'phone_number_ar': to_arabic_digits(data.get('phone_number', '')),
            'plate_number_ar': to_arabic_digits(data.get('plate_number', '')),
        }
        
        template_map = {
            'warning_letter': 'shared/print/warning_letter.html',
            'penalty_deduction': 'shared/print/penalty_deduction.html',
            'deliver_pledge': 'shared/print/deliver_pledge.html',
            'mobile_receiving': 'shared/print/deliver_pledge.html',
            'ack_receipt': 'shared/print/ack_receipt.html',
            'car_receipt': 'shared/print/car_receipt.html',
        }
        
        template_name = template_map.get(record.doc_type, 'shared/print_layout.html')
            
        return render(request, template_name, context)

class PreviewOperationDocumentView(StaffRequiredMixin, CompanyDataMixin, View):
    def post(self, request):
        from core.models import Driver, COMPANY_CHOICES
        import json
        from django.utils import timezone
        from core.models import SystemSettings
        
        try:
            data = json.loads(request.body)
        except:
            data = {}
            
        driver_id = data.get('driver_id')
        doc_type = data.get('doc_type') or data.get('docType')
        
        driver = None
        if driver_id:
            try:
                driver = self.get_queryset_by_company(Driver).get(id=driver_id)
            except Driver.DoesNotExist:
                pass
                
        def to_arabic_digits(text):
            if not text: return ''
            text = str(text)
            arabic_digits = {'0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤', '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'}
            for eng, ar in arabic_digits.items():
                text = text.replace(eng, ar)
            return text
            
        now = timezone.now()
        date_en = data.get('doc_date') or now.strftime('%Y-%m-%d')
        date_ar = to_arabic_digits(date_en)
        try:
            from datetime import datetime
            dt = datetime.strptime(date_en, '%Y-%m-%d')
            date_month_en = dt.strftime('%B %Y')
        except:
            date_month_en = now.strftime('%B %Y')
        date_month_ar = to_arabic_digits(date_month_en)
        
        system_settings = SystemSettings.objects.first()
        company_name = system_settings.brand_name if system_settings else data.get('company_name', '')
        company_name_ar = data.get('company_name_ar', '')
        
        company_logo_url = None
        if system_settings and system_settings.logo:
            company_logo_url = system_settings.logo.url
                
        # Mock a record for the template
        class MockRecord:
            def __init__(self, doc_type):
                self.doc_type = doc_type
        
        record = MockRecord(doc_type)
                
        context = {
            'record': record,
            'driver': driver,
            'data': data,
            'auto_print': False,
            'date_en': data.get('formatted_date') or date_en,
            'date_ar': data.get('formatted_date_ar') or date_ar,
            'date_month_en': data.get('formatted_date_month') or date_month_en,
            'date_month_ar': data.get('formatted_date_month_ar') or date_month_ar,
            'company_name': company_name,
            'company_name_ar': data.get('company_name_ar') or company_name_ar,
            'company_logo_url': company_logo_url,
            'driver_name_ar': data.get('driver_name_ar', ''),
            'civil_id_ar': to_arabic_digits(data.get('civil_id_number_ar', driver.civil_id_number if driver else '')),
            'deduction_amount_ar': to_arabic_digits(data.get('deduction_amount', '00.00')),
            'inst1_amount_ar': to_arabic_digits(data.get('inst1_amount', '00.00')),
            'inst2_amount_ar': to_arabic_digits(data.get('inst2_amount', '00.00')),
            'inst3_amount_ar': to_arabic_digits(data.get('inst3_amount', '00.00')),
            'inst4_amount_ar': to_arabic_digits(data.get('inst4_amount', '00.00')),
            'serial_number_ar': to_arabic_digits(data.get('serial_number', '')),
            'phone_number_ar': to_arabic_digits(data.get('phone_number', '')),
            'plate_number_ar': to_arabic_digits(data.get('plate_number', '')),
        }
        
        template_map = {
            'warning_letter': 'shared/print/warning_letter.html',
            'penalty_deduction': 'shared/print/penalty_deduction.html',
            'deliver_pledge': 'shared/print/deliver_pledge.html',
            'mobile_receiving': 'shared/print/deliver_pledge.html',
            'ack_receipt': 'shared/print/ack_receipt.html',
            'car_receipt': 'shared/print/car_receipt.html',
        }
        
        template_name = template_map.get(doc_type, 'shared/print_layout.html')
        return render(request, template_name, context)

class DeleteOperationDocumentView(StaffRequiredMixin, CompanyDataMixin, View):
    def post(self, request, pk):
        from core.models import OperationDocumentHistory
        record = get_object_or_404(self.get_queryset_by_company(OperationDocumentHistory), pk=pk)
        
        # Optionally restrict employees to only delete their own records
        if request.user.role == 'employee' and record.creator != request.user:
            return redirect('access_denied')
            
        record.delete()
        django_messages.success(request, 'Document record deleted successfully.')
        return redirect('operation_documents')

from django.db.models import Sum

class PnLDashboardView(AdminManagerRequiredMixin, CompanyDataMixin, View):
    def get(self, request):
        from core.models import DriverExpense, Company, Driver
        import json
        
        # Base querysets
        user = self.request.user
        expenses_qs = self.get_queryset_by_company(DriverExpense, company_field='driver__company')
        
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            expenses_qs = expenses_qs.filter(date__gte=start_date)
        if end_date:
            expenses_qs = expenses_qs.filter(date__lte=end_date)
            
        if user.is_superuser and not user.company:
            companies_qs = Company.objects.all()
        else:
            companies_qs = Company.objects.filter(id=user.company.id) if user.company else Company.objects.none()
        drivers_qs = self.get_queryset_by_company(Driver)
        
        # Contract-wise Expenses
        contract_expenses = {}
        # Get all distinct contract types from drivers in this company
        from core.models import CONTRACT_CHOICES
        contract_types = dict(CONTRACT_CHOICES)
        for c_key, c_name in contract_types.items():
            total = expenses_qs.filter(driver__contract_type=c_key).aggregate(Sum('total_expense'))['total_expense__sum'] or 0
            contract_expenses[c_name] = float(total)
            
        # Driver-wise Expenses
        driver_expenses = {}
        for d in drivers_qs:
            agg = expenses_qs.filter(driver=d).aggregate(
                Sum('petrol'), Sum('oil_change'), Sum('repair_vehicle'),
                Sum('room_rent'), Sum('sim_recharge'), Sum('car_rent'),
                Sum('emp_salary'), Sum('total_expense')
            )
            driver_expenses[str(d.id)] = {
                'name': d.full_name,
                'total': float(agg['total_expense__sum'] or 0),
                'breakdown': [
                    float(agg['petrol__sum'] or 0),
                    float(agg['oil_change__sum'] or 0),
                    float(agg['repair_vehicle__sum'] or 0),
                    float(agg['room_rent__sum'] or 0),
                    float(agg['sim_recharge__sum'] or 0),
                    float(agg['car_rent__sum'] or 0),
                    float(agg['emp_salary__sum'] or 0)
                ]
            }
            
        drivers_json = json.dumps([
            {'id': str(d.id), 'full_name': d.full_name, 'civil_id_number': d.civil_id_number}
            for d in drivers_qs.filter(is_active=True)
        ])
        
        context = {
            'start_date': start_date or '',
            'end_date': end_date or '',
            'contract_names_json': json.dumps(list(contract_expenses.keys())),
            'contract_totals_json': json.dumps(list(contract_expenses.values())),
            'driver_expenses_json': json.dumps(driver_expenses),
            'drivers_json': drivers_json
        }
        return render(request, 'shared/pnl.html', context)

class ExpenseAddView(AdminManagerRequiredMixin, CompanyDataMixin, View):
    def post(self, request):
        import json
        from django.http import JsonResponse
        from core.models import Driver, DriverExpense
        
        try:
            data = json.loads(request.body)
        except:
            data = {}
            
        driver_id = data.get('driver_id')
        if not driver_id:
            return JsonResponse({'error': 'Driver is required'}, status=400)
            
        try:
            driver = self.get_queryset_by_company(Driver).get(id=driver_id)
        except Driver.DoesNotExist:
            return JsonResponse({'error': 'Driver not found'}, status=404)
            
        try:
            petrol = float(data.get('petrol') or 0)
            oil_change = float(data.get('oil_change') or 0)
            repair_vehicle = float(data.get('repair_vehicle') or 0)
            room_rent = float(data.get('room_rent') or 0)
            sim_recharge = float(data.get('sim_recharge') or 0)
            car_rent = float(data.get('car_rent') or 0)
            emp_salary = float(data.get('emp_salary') or 0)
        except ValueError:
            return JsonResponse({'error': 'Invalid numeric values'}, status=400)
            
        DriverExpense.objects.create(
            driver=driver,
            company=driver.company,
            petrol=petrol,
            oil_change=oil_change,
            repair_vehicle=repair_vehicle,
            room_rent=room_rent,
            sim_recharge=sim_recharge,
            car_rent=car_rent,
            emp_salary=emp_salary,
            created_by=request.user
        )
        return JsonResponse({'success': True})
