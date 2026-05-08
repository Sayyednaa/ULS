import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.jpeg', '.xlsx', '.xls', '.csv']
    
    # Extension check
    if ext not in valid_extensions:
        allowed_str = ", ".join([e.strip('.').upper() for e in valid_extensions])
        raise ValidationError(f'Unsupported file extension. Allowed: {allowed_str}')

    # Size check
    filesize = value.size
    is_excel = ext in ['.xlsx', '.xls', '.csv']
    limit = 20 * 1048576 if is_excel else 1048576 # 20MB for excel, 1MB for others
    
    if filesize > limit:
        limit_mb = int(limit / 1048576)
        raise ValidationError(f"The maximum file size for {ext.strip('.').upper()} files is {limit_mb}MB")
