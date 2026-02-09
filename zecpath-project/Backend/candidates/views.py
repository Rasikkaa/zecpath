from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.permissions import IsCandidate, IsAdmin
from .models import Candidate
from .serializers import CandidateProfileSerializer, ResumeUploadSerializer
from .services import CandidateService
from core.exceptions import APIResponse
from common.services.resume_parser import ResumeParser
from common.services.resume_analyzer import ResumeAnalyzer

class CandidateProfileAPI(APIView):
    permission_classes = [IsCandidate | IsAdmin]
    
    def get(self, request):
        try:
            if request.user.role == 'admin':
                candidate_id = request.GET.get('id')
                if candidate_id:
                    candidate = Candidate.objects.get(id=candidate_id)
                else:
                    return Response({'error': 'Candidate ID required for admin'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                candidate = Candidate.objects.get(user=request.user)
            serializer = CandidateProfileSerializer(candidate, context={'request': request})
            return Response(serializer.data)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate profile not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        candidate, error = CandidateService.update_candidate_profile(request.user, request.data)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CandidateProfileSerializer(candidate, context={'request': request})
        return Response(serializer.data)
    
    def patch(self, request):
        return self.put(request)
    
    def delete(self, request):
        try:
            candidate = Candidate.objects.get(user=request.user)
            user = candidate.user
            candidate.delete()
            user.delete()
            return Response({'message': 'Profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate profile not found'}, status=status.HTTP_400_BAD_REQUEST)

class ResumeUploadAPI(APIView):
    permission_classes = [IsCandidate]
    
    def post(self, request):
        file = request.FILES.get('resume')
        candidate, error = CandidateService.upload_resume(request.user, file)
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Resume uploaded successfully',
            'resume_url': request.build_absolute_uri(candidate.resume.url) if candidate.resume else None
        }, status=status.HTTP_200_OK)

class ResumeDeleteAPI(APIView):
    permission_classes = [IsCandidate]
    
    def delete(self, request):
        success, message = CandidateService.delete_resume(request.user)
        
        if success:
            return Response({'message': message})
        return Response({'error': message}, status=status.HTTP_404_NOT_FOUND)

class ResumeDownloadAPI(APIView):
    permission_classes = [IsCandidate | IsAdmin]
    
    def get(self, request, candidate_id=None):
        response, error = CandidateService.download_resume(request.user, candidate_id)
        
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        
        return response

class ResumeParseAPI(APIView):
    permission_classes = [IsCandidate]
    
    def post(self, request):
        try:
            candidate = Candidate.objects.get(user=request.user)
            
            if not candidate.resume:
                return Response({'error': 'No resume uploaded'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Analyze resume with NLP
            structured_data, error = ResumeAnalyzer.analyze_resume(candidate.resume.path)
            
            if error:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate resume score
            resume_score = ResumeAnalyzer.calculate_resume_score(structured_data)
            
            # Get ML-ready format
            ml_format = ResumeAnalyzer.get_ml_ready_format(structured_data)
            
            return Response({
                'structured_data': structured_data,
                'resume_score': resume_score,
                'ml_ready_format': ml_format,
                'file_info': {
                    'file_name': candidate.resume.name,
                    'file_size': candidate.resume.size
                }
            })
            
        except Candidate.DoesNotExist:
            return Response({'error': 'Candidate profile not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Analysis failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)