from rest_framework import serializers
from .models import Employer, Job

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['company_name', 'website', 'domain', 'company_description', 'company_size', 'verification']

class EmployerProfileSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Employer
        fields = ['id', 'company_name', 'website', 'domain', 'company_description', 'company_size', 'verification', 'user_info']
    
    def get_user_info(self, obj):
        return {
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }

class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    publisher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'skills', 'experience', 'salary_min', 'salary_max', 'location', 'job_type', 'status', 'is_featured', 'created_at', 'updated_at', 'company_name', 'publisher_name']
        read_only_fields = ['id', 'created_at', 'updated_at', 'company_name', 'publisher_name']
    
    def get_company_name(self, obj):
        return obj.employer.company_name
    
    def get_publisher_name(self, obj):
        return f"{obj.employer.user.first_name} {obj.employer.user.last_name}".strip()