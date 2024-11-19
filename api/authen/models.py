from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _ 
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from .user_manager import UserManager
from datetime import date
from rest_framework_simplejwt.tokens import RefreshToken
import random
import string
from datetime import timedelta

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, verbose_name=_("Email Address"))
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))

    # Additional info
    date_of_birth = models.DateField(
        validators=[
            MinValueValidator(date(1943, 1, 1)),
            MaxValueValidator(timezone.now().date())
        ],
        default=timezone.now, 
        verbose_name="Date of Birth"
    )
    resident_id = models.CharField(
        max_length=10,
        null=True,
        default='None',
        unique=True,
        verbose_name=_("Resident ID")
    )
    staff_id = models.CharField(
        max_length=10,
        null=True,
        default='None',
        unique=True,
        verbose_name=_("staff ID")
    )
    role = models.CharField(
        max_length=50,
        verbose_name=_("Role")
    )


    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
    
    @property
    def get_full_name(self):
        return f'{self.last_name} {self.first_name}'
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    def get_dummy_user(self):
        if not self.objects.filter(username='anonymous').exists():
            self.objects.create_user(
                username='anonymous',
                email='anonymous@example.com',
                password='dummy_password'
            )
        return self.objects.filter(username='anonymous')


class OneTimePassword(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    code=models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self) -> str:
        return f"{self.user.email}--passcode"
    
    def generate_code(self):
        self.code = ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Check if the OTP is expired (e.g., expires after 5 minutes)"""
        return (self.created_at + timedelta(minutes=5)) < timezone.now()
    
