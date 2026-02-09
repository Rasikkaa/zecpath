from rest_framework import serializers
from .models import Candidate

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['skills', 'education', 'experience', 'expected_salary', 'experience_years', 'resume']

class ResumeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['resume']
    
    def validate_resume(self, value):
        if not value:
            raise serializers.ValidationError("Resume file is required")
        return value

class CandidateProfileSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = ['skills', 'education', 'experience', 'expected_salary', 'experience_years', 'resume', 'resume_url', 'user_info']
    
    def get_user_info(self, obj):
        return {
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }
    
    def get_resume_url(self, obj):
        if obj.resume:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.resume.url)
        return None