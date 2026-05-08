from .models import SystemSettings
from django.conf import settings

def system_settings(request):
    """
    Context processor to make brand name and logo available in all templates.
    """
    try:
        settings_obj = SystemSettings.objects.first()
        if not settings_obj:
            # Fallback to defaults if no record exists
            return {
                'brand_name': 'SAYEDNA LOGISTICS',
                'brand_logo': settings.STATIC_URL + 'img/logo.png',
            }
        
        return {
            'brand_name': settings_obj.brand_name,
            'brand_logo': settings_obj.logo.url if settings_obj.logo else settings.STATIC_URL + 'img/logo.png',
            'max_excel_mb': settings_obj.max_excel_size_mb,
            'max_other_mb': settings_obj.max_other_size_mb,
        }
    except:
        # Emergency fallback if database is not ready
        return {
            'brand_name': 'SAYEDNA LOGISTICS',
            'brand_logo': settings.STATIC_URL + 'img/logo.png',
            'max_excel_mb': 20,
            'max_other_mb': 1,
        }
