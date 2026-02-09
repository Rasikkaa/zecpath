import os
import re
from django.http import HttpResponse
from django.core.files.storage import default_storage
from candidates.models import Candidate


class FileService:
    """Service class for secure file operations"""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent security issues"""
        if not filename:
            return "resume"
        
        # Remove path separators and dangerous characters
        filename = os.path.basename(filename)
        # Remove or replace dangerous characters including newlines
        filename = re.sub(r'[^\w\s.-]', '', filename)
        # Remove multiple spaces and replace with single space
        filename = re.sub(r'\s+', ' ', filename).strip()
        # Limit length
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:95] + ext
        
        return filename or "resume"
    
    @staticmethod
    def validate_file(file):
        """Validate uploaded file"""
        if not file:
            return False, "No file provided"
        
        # Check file size
        if file.size > FileService.MAX_FILE_SIZE:
            return False, f"File size exceeds {FileService.MAX_FILE_SIZE // (1024*1024)}MB limit"
        
        # Check file extension
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in FileService.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Allowed types: {', '.join(FileService.ALLOWED_EXTENSIONS)}"
        
        return True, None
    
    @staticmethod
    def upload_resume(user, file):
        """Upload resume file for candidate"""
        try:
            candidate = Candidate.objects.get(user=user)
        except Candidate.DoesNotExist:
            return None, "Candidate profile not found"
        
        # Validate file
        is_valid, error = FileService.validate_file(file)
        if not is_valid:
            return None, error
        
        # Delete old resume if exists
        if candidate.resume:
            try:
                if os.path.exists(candidate.resume.path):
                    os.remove(candidate.resume.path)
            except (OSError, ValueError):
                pass  # Continue even if old file deletion fails
        
        # Save new resume
        candidate.resume = file
        candidate.save()
        
        return candidate, None
    
    @staticmethod
    def delete_resume(user):
        """Delete resume file for candidate"""
        try:
            candidate = Candidate.objects.get(user=user)
        except Candidate.DoesNotExist:
            return False, "Candidate profile not found"
        
        if not candidate.resume:
            return False, "No resume found"
        
        try:
            if os.path.exists(candidate.resume.path):
                os.remove(candidate.resume.path)
        except (OSError, ValueError) as e:
            return False, f"Error deleting file: {str(e)}"
        
        candidate.resume = None
        candidate.save()
        return True, "Resume deleted successfully"
    
    @staticmethod
    def download_resume(user, candidate_id=None):
        """Download resume file with proper security checks"""
        try:
            if user.role == 'candidate':
                candidate = Candidate.objects.get(user=user)
            else:
                if not candidate_id:
                    return None, "Candidate ID required"
                candidate = Candidate.objects.get(id=candidate_id)
        except Candidate.DoesNotExist:
            return None, "Candidate not found"
        
        if not candidate.resume:
            return None, "No resume found"
        
        try:
            if not os.path.exists(candidate.resume.path):
                return None, "Resume file not found on server"
            
            # Sanitize filename for response
            original_filename = os.path.basename(candidate.resume.name)
            safe_filename = FileService.sanitize_filename(original_filename)
            
            # Get file extension for content type
            ext = os.path.splitext(safe_filename)[1].lower()
            content_type = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }.get(ext, 'application/octet-stream')
            
            with open(candidate.resume.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                # Use safe filename in Content-Disposition header
                response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
                return response, None
                
        except (OSError, IOError) as e:
            return None, f"Error reading file: {str(e)}"