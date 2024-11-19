from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'date_of_birth', 'resident_id', 'staff_id', 'role', 'password', 'password2']
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        user.save()
        return user
    
class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True) 
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'date_of_birth', 'resident_id', 'staff_id', 'role']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid credentials')

        if not user.check_password(password):
            raise AuthenticationFailed('Invalid credentials')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive')

        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Return the tokens as a dictionary
        return {
            'access': str(access_token),
            'refresh': str(refresh),
        }

class PasswordVerificationSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirm password must match.")
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})

        return data
    
class EmailVerificationSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_email = serializers.EmailField(write_only=True)

    def validate(self, data):
        if data['new_email'] == data['user_email']:
            raise serializers.ValidationError("New email address must be different from the current email.")
        return data


