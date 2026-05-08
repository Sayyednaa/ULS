import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    from .models import SystemSettings
    
    # Get dynamic limits from settings
    settings_obj = SystemSettings.objects.first()
    max_excel_mb = settings_obj.max_excel_size_mb if settings_obj else 20
    max_other_mb = settings_obj.max_other_size_mb if settings_obj else 1

    ext = '.' + value.name.split('.')[-1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.jpeg', '.xlsx', '.xls', '.csv']
    excel_extensions = ['.xlsx', '.xls', '.csv']
    
    if ext not in valid_extensions:
        raise ValidationError(f'Unsupported file extension. Allowed: {", ".join(valid_extensions)}')

    # Size Validation (Dynamic)
    limit_mb = max_excel_mb if ext in excel_extensions else max_other_mb
    if value.size > limit_mb * 1048576:
        raise ValidationError(f'File too large. Maximum size allowed for {ext.upper()} is {limit_mb}MB.')
