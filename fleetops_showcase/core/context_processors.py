from .models import SystemSettings
from django.conf import settings

def system_settings(request):
    """
    Context processor to make brand name and logo available in all templates.
    Prioritizes the logged-in user's company settings.
    """
    data = {
        'brand_name': 'Unpredictable Logistics Solutions',
        'brand_logo': settings.STATIC_URL + 'img/logo.png',
        'max_excel_mb': 20,
        'max_other_mb': 1,
    }
    
    try:
        settings_obj = SystemSettings.objects.first()
        if settings_obj:
            data['brand_name'] = settings_obj.brand_name
            if settings_obj.logo:
                data['brand_logo'] = settings_obj.logo.url
            data['max_excel_mb'] = settings_obj.max_excel_size_mb
            data['max_other_mb'] = settings_obj.max_other_size_mb
    except Exception:
        pass

    # Override with company-specific branding
    if request.user.is_authenticated:
        company = getattr(request.user, 'company', None)
        if company:
            data['brand_name'] = company.name
            if company.logo:
                data['brand_logo'] = company.logo.url
            
    return data
