from django.contrib.auth.base_user import BaseUserManager

# importing typing for type hinting
from typing import Any

# creating a custom manager for User

class UserManager(BaseUserManager):
    # to create normal user
    def create_user(self,email:str,password:str,**extra_fields:Any):
        if not email:
            raise ValueError("Provide a valid email")
        # to normalize the email
        email=self.normalize_email(email=email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    # to create superuser/admin
    def create_superuser(self,email:str,password:str,**extra_fields:Any):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)
        
