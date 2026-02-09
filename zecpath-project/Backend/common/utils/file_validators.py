import os
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

@deconstructible
class FileValidator:
    def __init__(self, max_size=5*1024*1024, allowed_extensions=None):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions or ['.pdf', '.doc', '.docx']
    
    def __call__(self, file):
        # Size validation
        if file.size > self.max_size:
            raise ValidationError(f'File size must be under {self.max_size/1024/1024}MB')
        
        # Extension validation
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(f'File type not allowed. Use: {", ".join(self.allowed_extensions)}')

def resume_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'resumes/{instance.user.id}_{instance.user.email.split("@")[0]}{ext}'