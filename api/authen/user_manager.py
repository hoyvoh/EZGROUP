from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _ 

class UserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("invalid email address"))
        
    def create_user(self, email, first_name, last_name, password, 
                    **extra_fields):
        if email:
            email=self.normalize_email(email)
            self.email_validator(email=email)
        
        else:
            raise ValueError(_("empty email address is not allowed"))
        
        if not first_name:
            raise ValueError(_("empty first name address is not allowed"))

        if not last_name:
            raise ValueError(_("empty last name address is not allowed"))
        
        user = self.model(email=email,
                          first_name=first_name,
                          last_name=last_name,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email,first_name, last_name, password, 
                         **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("you must be a staff before being an admin"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("you must be a superuser before being an admin"))
        
        user = self.create_user(
            email,first_name, last_name, password, 
            **extra_fields
        )
        return user