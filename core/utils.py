from core.models import Notification, Profile

def notify_superadmin_action(superadmin, action_type, description, related_driver=None):
    """
    Notifies relevant stakeholders (Managers, Accountants) when a superadmin performs a core action.
    """
    if superadmin.role != 'superadmin':
        return

    # Find stakeholders
    stakeholders = Profile.objects.filter(role__in=['manager', 'accountant'])
    
    for user in stakeholders:
        Notification.objects.create(
            user=user,
            title=f"Superadmin Action: {action_type}",
            body=f"{superadmin.get_full_name()} {description}.",
            type='system',
            related_driver=related_driver
        )

def check_and_notify_expiries(user):
    """
    Checks for expiring documents and notifies the user if they are a manager or admin.
    """
    if user.role not in ['manager', 'admin', 'superadmin']:
        return

    from core.models import Driver, Notification
    from datetime import date, timedelta
    
    # We'll check for expiries within 30 days
    warning_threshold = 30
    drivers = Driver.objects.filter(is_active=True)
    
    for driver in drivers:
        expiring = driver.get_expiring_documents(days=warning_threshold)
        for doc in expiring:
            title = f"Expiry Alert: {doc['label']}"
            
            if doc['status'] in ['warning', 'expired']:
                body = f"The {doc['label']} for driver {driver.full_name} is {doc['status'].upper()}. (Expiry: {doc['expiry'] or 'Missing'})"
                
                # Avoid duplicates
                exists = Notification.objects.filter(
                    user=user,
                    related_driver=driver,
                    title=title,
                    is_read=False
                ).exists()
                
                if not exists:
                    Notification.objects.create(
                        user=user,
                        title=title,
                        body=body,
                        type='document_expiry',
                        related_driver=driver
                    )
            else:
                # If the document is now fixed (OK) or missing (resolved from warning), clear alerts
                Notification.objects.filter(
                    user=user,
                    related_driver=driver,
                    title=title,
                    is_read=False
                ).delete()

def check_operation_documents_expiries(user):
    from core.models import OperationDocumentHistory, Notification
    from datetime import date
    
    today = date.today()
    
    # Get all operation documents created by this user that are due and haven't been notified yet
    expired_docs = OperationDocumentHistory.objects.filter(
        creator=user,
        due_date__lte=today,
        is_expired_notification_sent=False
    )
    
    for doc in expired_docs:
        doc_type_display = doc.get_doc_type_display()
        driver_name = doc.driver.full_name
        title = f"Document Expired: {doc_type_display}"
        body = f"The {doc_type_display} document for driver {driver_name} has expired."
        
        Notification.objects.create(
            user=user,
            title=title,
            body=body,
            type='document_expiry',
            related_driver=doc.driver
        )
        
        # Mark as sent
        doc.is_expired_notification_sent = True
        doc.save()
