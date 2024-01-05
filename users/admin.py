from django.contrib import admin
from .models import User
# Register your models here.

# to register my model with admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display=["name","email","profile_picture"]

