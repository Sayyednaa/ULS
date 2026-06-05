from django.urls import path
from . import views

urlpatterns = [
    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/bulk-save/', views.InvoiceBulkSaveView.as_view(), name='invoice_bulk_save'),
    path('invoices/reset/', views.InvoiceResetView.as_view(), name='invoice_reset'),
    path('invoices/add/', views.InvoiceAddView.as_view(), name='invoice_add'),
    path('invoices/<uuid:pk>/edit/', views.InvoiceEditView.as_view(), name='invoice_edit'),
    path('invoices/<uuid:pk>/delete/', views.InvoiceDeleteView.as_view(), name='invoice_delete'),
    path('invoices/archive/', views.InvoiceArchiveActionView.as_view(), name='invoice_archive_action'),
    path('invoices/export/', views.InvoiceExportView.as_view(), name='invoice_export'),

    # Archive
    path('archive/', views.ArchiveListView.as_view(), name='archive_list'),
    path('archive/export/', views.ArchiveExportView.as_view(), name='archive_export'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<uuid:pk>/read/', views.NotificationReadView.as_view(), name='notification_read'),
    path('notifications/read-all/', views.NotificationReadAllView.as_view(), name='notification_read_all'),
    path('notifications/clear-all/', views.NotificationClearAllView.as_view(), name='notification_clear_all'),

    # Messages
    path('messages/', views.MessageInboxView.as_view(), name='message_inbox'),
    path('messages/compose/', views.MessageComposeView.as_view(), name='message_compose'),
    path('messages/<uuid:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/<uuid:pk>/read/', views.MessageReadView.as_view(), name='message_read'),

    # Contact
    path('contact/', views.ContactView.as_view(), name='contact'),

    # Tasks
    path('tasks/add/', views.TaskAddView.as_view(), name='task_add'),
    path('tasks/assign/', views.TaskAssignView.as_view(), name='task_assign'),
    path('tasks/<uuid:pk>/toggle/', views.TaskToggleView.as_view(), name='task_toggle'),
    path('tasks/<uuid:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),

    # Archive Extras
    path('archive/company-files/', views.CompanyFileListView.as_view(), name='company_files'),
    path('archive/company-files/<uuid:pk>/edit/', views.CompanyFileUpdateView.as_view(), name='company_file_edit'),
    path('archive/company-files/<uuid:pk>/delete/', views.CompanyFileDeleteView.as_view(), name='company_file_delete'),
    path('archive/deactivated-drivers/', views.DeactivatedDriversView.as_view(), name='deactivated_drivers'),

    # Drivers Receivings
    path('drivers/receivings/', views.DriverReceivingsView.as_view(), name='driver_receivings'),
    path('drivers/receivings/<uuid:pk>/delete/', views.DriverReceivingsDeleteView.as_view(), name='driver_receivings_delete'),

    path('bulk/template/<str:model_type>/', views.TemplateDownloadView.as_view(), name='template_download'),
    path('bulk/upload/<str:model_type>/', views.BulkUploadView.as_view(), name='bulk_upload'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('operation-documents/', views.OperationDocumentsView.as_view(), name='operation_documents'),
    path('operation-documents/save/', views.SaveOperationDocumentView.as_view(), name='save_operation_document'),
    path('operation-documents/print/', views.PrintOperationDocumentView.as_view(), name='print_operation_document'),
    path('operation-documents/<uuid:pk>/delete/', views.DeleteOperationDocumentView.as_view(), name='delete_operation_document'),
]
