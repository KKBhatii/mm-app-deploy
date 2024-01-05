from django import forms
from .models import User


# Login form for the user
class LoginForm(forms.Form):
    email=forms.EmailField(required=True,widget=forms.EmailInput(attrs={"placeholder":"Enter your Email..."}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Enter yor password..."}))


# Signup form for the user
class SignupForm(forms.Form):
    email=forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder":"Enter your Email..."}))
    name=forms.CharField(label=None, widget=forms.TextInput(attrs={"placeholder":"Enter your Name..."}))


# to create user
class CreateUserForm(forms.Form):
    confirm_password=forms.CharField(label=None,help_text="Confirm Password", widget=forms.PasswordInput(attrs={"placeholder":"Confirm your Password..."}))
    password=forms.CharField(label=None, widget=forms.PasswordInput(attrs={"placeholder":"Enter your Password..."}))


# form to update the user profile
class ProfileUpdateForm(forms.Form):
    name=forms.CharField(required=True)
    email=forms.EmailField(required=True)
    contact_no=forms.CharField(required=False)
    profile_picture=forms.ImageField(required=False,widget=forms.ClearableFileInput(attrs={"hidden":True}))
    
    # constructor with the user instance
    def __init__(self,user_instance:User,*args, **kwargs):
        self.user_instance=user_instance
        super().__init__(*args, **kwargs)
        
        
    def save(self):
        # Update the user profile with the form data
        self.user_instance.name = self.cleaned_data["name"]
        self.user_instance.email = self.cleaned_data["email"]
        self.user_instance.contact_no = self.cleaned_data["contact_no"]

        if self.cleaned_data["contact_no"]:
            self.user_instance.contact_no = self.cleaned_data["contact_no"]

        if self.cleaned_data["profile_picture"]:
            self.user_instance.profile_picture = self.cleaned_data["profile_picture"]

        self.user_instance.save()
    


