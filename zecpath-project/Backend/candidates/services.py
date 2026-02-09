from .models import Candidate
from .serializers import CandidateProfileSerializer
from common.services.file_service import FileService

class CandidateService:
    @staticmethod
    def get_candidate_profile(user):
        try:
            candidate = Candidate.objects.get(user=user)
            return candidate, None
        except Candidate.DoesNotExist:
            return None, "Candidate profile not found"
    
    @staticmethod
    def update_candidate_profile(user, data):
        try:
            candidate = Candidate.objects.get(user=user)
            serializer = CandidateProfileSerializer(candidate, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return candidate, None
            return None, serializer.errors
        except Candidate.DoesNotExist:
            return None, "Candidate profile not found"
    
    @staticmethod
    def upload_resume(user, file):
        return FileService.upload_resume(user, file)
    
    @staticmethod
    def delete_resume(user):
        return FileService.delete_resume(user)
    
    @staticmethod
    def download_resume(user, candidate_id=None):
        return FileService.download_resume(user, candidate_id)