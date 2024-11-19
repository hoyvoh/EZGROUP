from django.contrib import admin
from django.urls import path
from authen.views import UserRegisterView, UserUpdateView, LogoutView, UserLoginView, VerifyOTPView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verification/otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('update/', UserUpdateView.as_view(), name='account-update'),
    path('account/login/', UserLoginView.as_view(), name='login'),
    path('token/',TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('account/logout/', LogoutView.as_view(), name='logout'),
]