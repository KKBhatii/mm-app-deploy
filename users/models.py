
# imports to generate a unique name for every upload
import os, uuid,time,datetime

from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from marketmate.settings import UPLOAD_URL
from .manager import UserManager

# importing typing for type hinting
from typing import Any

# to generate a unique name for every upload
def generate_filename(instance:Any,filename:str)->str:
    ext=filename.split(".")[1]
    unique_name = f"image-{uuid.uuid4()}.{ext}"
    return os.path.join(f"{UPLOAD_URL}images/users/", unique_name)


def generate_unique_id()->str:
    id= f"{time.time()}-{uuid.uuid4()}"
    return id[:20]


class User(AbstractBaseUser,PermissionsMixin):

    # validate the file upload type
    image_file_validator = FileExtensionValidator(
        allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'bmp'],
        message='Only image files (jpg, jpeg, png, gif, bmp) are allowed.'
    )

    id=models.CharField(default=generate_unique_id,unique=True,primary_key=True,
                        editable=False, max_length=255)
    name=models.CharField( max_length=100)
    email=models.CharField(max_length=254,unique=True,null=False)
    contact_no=models.CharField(max_length=15,null=True,default=None,)

    is_superuser=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)

    profile_picture = models.ImageField(upload_to=generate_filename, max_length=350, null=True, default=None,
                                      validators=[image_file_validator],blank=True)

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=["name"]

    # to delete the previous image, if any
    def save(self,*args:Any, **kwargs:Any)->None:
        if self.id:
            previous_instance=User.objects.filter(id=self.id).first()
            # deleting only if a new image is uploaded
            if self.profile_picture and previous_instance.profile_picture and self.profile_picture!=previous_instance.profile_picture:
                previous_instance.profile_picture.delete()
            super().save(*args, **kwargs)

    # to initialize objects as user manager
    objects=UserManager()

    class Meta:
        db_table="user"

        def __str__(self) -> str:
            return self.name
        
class VerificationTokens(models.Model):
    name=models.CharField(null=False,default=None,max_length=50)
    email=models.CharField(null=False,max_length=50)
    token=models.CharField(null=False,max_length=50)
    created_at=models.DateTimeField(default=datetime.datetime.now)
