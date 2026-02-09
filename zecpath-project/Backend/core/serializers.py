from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Application, AuditLog

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'role', 'first_name', 'last_name', 'password', 'confirm_password']
    
    def validate(self, data):
        # Only check password confirmation if confirm_password is provided
        if 'confirm_password' in data and data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'role', 'is_verified', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

class ApplicationSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.user.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    resume_snapshot_url = serializers.SerializerMethodField()
    match_score = serializers.IntegerField(read_only=True)
    match_breakdown = serializers.JSONField(read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'
    
    def get_resume_snapshot_url(self, obj):
        if obj.resume_snapshot:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.resume_snapshot.url)
        return None

class AuditLogSerializer(serializers.ModelSerializer):
    admin_email = serializers.CharField(source='admin.email', read_only=True)
    admin_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = '__all__'
    
    def get_admin_name(self, obj):
        return f"{obj.admin.first_name} {obj.admin.last_name}".strip() or obj.admin.email