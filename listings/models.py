from django.db import models

# importing core modules to generate unique key
import os,uuid,time

# importing validators
from django.core.validators import FileExtensionValidator
from marketmate.settings import UPLOAD_URL

# importing user model
from users.models import User



# to generate a unique name for every upload
def generate_filename(instance,filename):
    ext=filename.split(".")[1]
    unique_name = f"image-{uuid.uuid4()}.{ext}"
    # return os.path.join(f"{UPLOAD_URL}images/listings/", unique_name)
    return os.path.join(unique_name)

# to generate a unique id against each item
def generate_unique_id():
    id= f"{time.time()}-{uuid.uuid4()}"
    return id[:20]

# creating listing model
class Listing(models.Model):
    id=models.CharField(default=generate_unique_id,unique=True,primary_key=True,
                        editable=False, max_length=255)
    title=models.CharField(max_length=150)
    description=models.TextField(null=True,default=None)
    category=models.CharField(max_length=100,null=False,default="Others")
    price=models.IntegerField(null=False,default=0)
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title
    


# creating model to store images related to a item
class ListingImages(models.Model):
    image_file_validator = FileExtensionValidator(
        allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp"],
        message="Only image files (jpg, jpeg, png, gif, bmp) are allowed."
    )
    item=models.ForeignKey(Listing,on_delete=models.CASCADE)
    image=models.ImageField(upload_to=generate_filename,max_length=350,null=True,default=None)

    # to compress and save the image
    def save(self,*args, **kwargs):
        super().save(*args, **kwargs)
