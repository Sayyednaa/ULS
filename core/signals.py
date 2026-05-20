from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='core.Driver')
def notify_on_driver_create(sender, instance, created, **kwargs):
    """Create notifications for staff when a new driver has document issues."""
    if created:
        from core.models import Notification, Profile
        staff = Profile.objects.filter(role__in=['admin', 'manager', 'employee'])
        docs = instance.get_expiring_documents()
        for doc in docs:
            if doc['status'] in ['warning', 'expired']:
                for user in staff:
                    Notification.objects.create(
                        user=user,
                        title=f"Document Alert: {doc['label']}",
                        body=(
                            f"{instance.full_name}'s {doc['label']} "
                            f"{'expires in ' + str(doc['days_remaining']) + ' days' if doc['status'] == 'warning' else 'has expired'}."
                        ),
                        type='document_expiry',
                        related_driver=instance,
                    )


@receiver(post_save, sender='core.MessageRecipient')
def notify_on_message(sender, instance, created, **kwargs):
    """Create notification when a user receives a new message."""
    if created:
        from core.models import Notification
        Notification.objects.create(
            user=instance.recipient,
            title=f"New message: {instance.message.subject}",
            body=f"From {instance.message.sender.get_full_name()}",
            type='new_message',
        )
