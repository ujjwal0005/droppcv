from rest_framework import serializers
from .models import EmployeeProfile, EmployerProfile, User, Service
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('name', 'password', 'password2', 'email', 'user_type', 'image')
        extra_kwargs = {
            'name': {'required': True},
            'user_type': {'required': True},
            'image': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def to_representation(self, instance):
        user = super().to_representation(instance)
        user.pop('password', None)
        user.pop('password2', None)
        token, _ = Token.objects.get_or_create(user=instance)
        user['token'] = token.key
        return user

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            name=validated_data['name'],
            email=validated_data['email'],
            user_type=validated_data['user_type'],
            image=validated_data.get('image', None),
            is_active=True
        )
        user.set_password(validated_data['password'])
        user.save()
        
        if user.user_type == 'employee':
            EmployeeProfile.objects.create(user=user)
        elif user.user_type == 'employer':
            EmployerProfile.objects.create(user=user)
        
        return user

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'user_type', 'image')

class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = '__all__'
        read_only_fields = ('user',)

class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = '__all__'
        read_only_fields = ('user',)

class UserSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileSerializer(read_only=True)
    employer_profile = EmployerProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('name', 'email', 'user_type', 'image', 'employee_profile', 'employer_profile')

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']
