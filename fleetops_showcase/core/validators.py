import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    # Size check (1MB Limit)
    filesize = value.size
    if filesize > 1048576:
        raise ValidationError("The maximum file size that can be uploaded is 1MB")

    # Extension check
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.jpeg', '.xlsx', '.xls', '.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed: PDF, DOC, DOCX, JPG, PNG, XLSX, XLS, CSV')
