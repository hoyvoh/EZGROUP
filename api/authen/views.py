from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from .models import User, OneTimePassword
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, UserUpdateSerializer, PasswordVerificationSerializer, EmailVerificationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

class UserRegisterView(generics.CreateAPIView):
    permission_classes=[AllowAny]
    serializer_class = UserRegisterSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save(is_active=False)
            
            otp_code = get_random_string(length=6, allowed_chars='0123456789')
            OneTimePassword.objects.create(user=user, code=otp_code)

            send_mail(
                'Account Verification OTP',
                f'Your OTP code to EZGROUP is: {otp_code}',
                settings.DEFAULT_FROM_EMAIL, 
                [user.email]
            )
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
            "detail": "User registered. Please check your email for the OTP to activate your account.",
            "access_token": access_token,
            "refresh_token": refresh_token
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp_code = request.data.get('otp')
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        otp_entry = OneTimePassword.objects.filter(user=user).last()
        if otp_entry is None:
            return Response({"detail": "No OTP found for this user."}, status=status.HTTP_400_BAD_REQUEST)
        if otp_code != otp_entry.code:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        otp_entry.delete()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "detail": "Account activated successfully. You can now log in.",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "accept": True,
        }, status=status.HTTP_200_OK)

class VerifyEmailView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            current_password = serializer.validated_data['current_password']
            new_email = serializer.validated_data['new_email']
            
            user = request.user

            user_authenticated = authenticate(username=user.email, password=current_password)
            if not user_authenticated:
                return Response({"detail": "Current password is incorrect."}, status=400)

            otp_code = get_random_string(length=6, allowed_chars='0123456789')
    
            otp = OneTimePassword.objects.create(user=user, code=otp_code)

            send_mail(
                subject="Your OTP Code for Email Verification",
                message=f"Your OTP code is {otp_code}",
                from_email="no-reply@yourdomain.com",
                recipient_list=[new_email],  
            )

            return Response({
                "detail": "OTP sent to your new email address. Please verify.",
                "otp_id": otp.id 
            }, status=202)
        else:
            return Response(serializer.errors, status=400)

class PasswordVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = PasswordVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            current_password = serializer.validated_data['current_password']
            if not user.check_password(current_password):
                return Response({"detail": "Current password is incorrect."}, status=400)
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password changed successfully."}, status=200)
        return Response(serializer.errors, status=400)

class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes=[IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)
        if serializer.is_valid(raise_exeption=True):
            serializer.save()
            return Response({"message": "User details updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = (AllowAny)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            tokens = user.tokens()
            return Response({"access":tokens['access'], "refresh":tokens['refresh']})
        else:
            return Response({"detail":"Invalid User"}, status=401)

class LogoutView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"detail": "Successfully logged out"}, status=205)
            except Exception as e:
                return Response({"detail": "Invalid refresh token"}, status=400)
        return Response({"detail": "No refresh token provided"}, status=400)
    
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        content = {'message': 'You have access to this protected view'}
        return Response(content)


