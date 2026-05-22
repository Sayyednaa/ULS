
from core.models import ROLE_CHOICES, DriverInvoice, MessageRecipient
from core.translations import TRANSLATIONS
import json

def global_context(request):
    """
    Global context processor for Unpredictable Logistics Solutions.
    Provides role information, unread counts, and translations.
    """
    context = {}
    
    # Language detection
    lang = getattr(request, 'LANGUAGE_CODE', 'en')[:2]
    context['lang'] = lang
    context['TRANSLATIONS_JSON'] = json.dumps(TRANSLATIONS)
    
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', 'driver')
        context['user_role'] = role
        
        # Unread notifications/messages counts
        # (Assuming these models have an 'is_read' or similar field)
        try:
            context['unread_notifications_count'] = request.user.notifications.filter(is_read=False).count()
            context['unread_messages_count'] = MessageRecipient.objects.filter(recipient=request.user, is_read=False).count()
        except Exception:
            context['unread_notifications_count'] = 0
            context['unread_messages_count'] = 0
            
    return context
