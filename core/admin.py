from django.contrib import admin
from .models import (
    Profile, Driver, DriverInvoice, InvoiceArchive,
    Deduction, Message, MessageRecipient, Notification, Task,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'company_name', 'contract_type', 'vehicle_type', 'is_active')
    list_filter = ('company_name', 'contract_type', 'vehicle_type', 'is_active')
    search_fields = ('full_name', 'phone', 'civil_id_number')


@admin.register(DriverInvoice)
class DriverInvoiceAdmin(admin.ModelAdmin):
    list_display = ('driver', 'specified_date', 'main_orders', 'hours')
    list_filter = ('specified_date',)


@admin.register(InvoiceArchive)
class InvoiceArchiveAdmin(admin.ModelAdmin):
    list_display = ('driver_name', 'archive_date', 'main_orders', 'hours')
    list_filter = ('archive_date',)


@admin.register(Deduction)
class DeductionAdmin(admin.ModelAdmin):
    list_display = ('driver', 'employee', 'deduction_date', 'contracting_company', 'contractor_deduction_kd')
    list_filter = ('contracting_company', 'deduction_date')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'created_at')


@admin.register(MessageRecipient)
class MessageRecipientAdmin(admin.ModelAdmin):
    list_display = ('message', 'recipient', 'is_read')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at')
    list_filter = ('status',)
