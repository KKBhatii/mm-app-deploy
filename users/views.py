# import typing 
from typing import Any

# importing timedelta and datetime from datetime
from datetime import timedelta,datetime

# importing render and http
from django.shortcuts import render
from django.http import HttpRequest,HttpResponse, HttpResponseRedirect as redirect

# importing email validator
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

# importing views
from django.views import View
from django.views.generic import TemplateView
from django.urls import reverse,reverse_lazy

# importing forms
from .forms import LoginForm,SignupForm,ProfileUpdateForm,CreateUserForm
from .models import User,VerificationTokens as Verification,generate_unique_id
from listings.models import Listing,ListingImages

# importing messages module for flash messages
from django.contrib import messages

# for authentication and login
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from marketmate.mailer import send_verification_mail

from functools import wraps

#importing GCS config functions
from marketmate.gcs_config import upload_file,generate_signed_url


# decorator to check if user is already logged in
def is_authenticated(redirect_url):
    def decorator(view_method):
        wraps(view_method) # to maintain the identity of the method
        def wrapper(instance,req:HttpRequest,*args, **kwargs):
            if req.user.is_authenticated:
                # if already logged in the redirecting to the homepage
                return redirect(redirect_to=reverse_lazy(redirect_url))
            return view_method(instance,req,*args, **kwargs)
        return wrapper
    return decorator
    

# to render signup page
class SignUpView(TemplateView):
    template_name="users/signup.html"
    form=SignupForm()
    @is_authenticated(redirect_url="home")
    def get(self,req:HttpRequest,*args:Any, **kwargs:Any)->HttpResponse:
        return super().get(req,*args,**kwargs)

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        # passing the form with the context
        context["signupForm"] =self.form 
        return context
    
class CreateUserView(TemplateView):
    template_name="users/create_user.html"
    form=CreateUserForm()
    @is_authenticated(redirect_url="home")
    def get(self,req:HttpRequest, token, *args:Any, **kwargs:Any)->HttpResponse:
        try:
            user_token= Verification.objects.get(token=token)
            # to expire the generated token after 30 minutes
            if user_token.created_at+timedelta(minutes=300)<datetime.now():
                user_token.delete()
                messages.error(req,message="Token Expired")
                return redirect(redirect_to=reverse_lazy("user_signup"))
            context=self.get_context_data(*args, **kwargs)
            context["token"]=token
            return self.render_to_response(context)
            # if token does not exist
        except Verification.DoesNotExist:
            messages.error(req,message="Invalid Url")
            return redirect(redirect_to=reverse_lazy("user_signup"))

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        # passing the form with the context
        context["form"] =self.form 
        return context
    



# to render login page
class LoginView(TemplateView):
    template_name="users/login.html"
    # creating object of the form
    form=LoginForm()
    @is_authenticated(redirect_url="home")
    def get(self, req: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(req, *args, **kwargs)
    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        # passing the form with the context
        context["loginForm"] =self.form 
        return context


class EditProfileView(TemplateView):
    template_name="users/edit_profile"

class UserView(View):
    # ---------------POST-------------------
    # to handle the User's post requests
    def post(self,req:HttpRequest, token:Any=None)->HttpResponse:
        if "create-session" in req.path:
            return self.create_session(req=req)
        if "create" in req.path:
            return self.create_user(req=req,token=token)
        if "update" in req.path:
            return self.update_user(req)
        return render(request=req,template_name="404.html")


        
        
    # to create a new user
    def create_user(self,req:HttpRequest,token:Any=None)->HttpResponse:
        try:
            if not token:
                form=SignupForm(data=req.POST)
                # if form data is valid
                if form.is_valid():
                    name,email=form.cleaned_data["name"],form.cleaned_data["email"]
                    email_validator=EmailValidator()
                    email_validator(email)

                    # checking if the user already exists in the database or not
                    is_user=User.objects.filter(email=email).exists()
                    # if the user already exists
                    if is_user:
                        messages.error(request=req,message="User already exists!")
                        return redirect(redirect_to=reverse_lazy("user_signup"))

                    verification_token=generate_unique_id()
                    to_verify_user=Verification(name=name,email=email,token=verification_token)
                    to_verify_user.save()
                    base_url = req.build_absolute_uri('/')
                    verification_url=f"{base_url}users/verify/{verification_token}"
                    # to send the verification mail
                    if send_verification_mail(send_to=email,user=name,verification_url=verification_url):
                        messages.success(request=req,message="Verification url sent on your mail!")
                        return redirect(redirect_to=reverse_lazy("user_signup"))

                messages.error(req, "Unable to Signup!")
                return redirect(redirect_to=reverse_lazy("user_signup"))
            else:
                verified_user=Verification.objects.get(token=token)
                form=CreateUserForm(data=req.POST)
                # if the form data is valid
                if form.is_valid():
                    password,confirm_password=form.cleaned_data["password"],form.cleaned_data["confirm_password"]
                    if password!=confirm_password:
                        messages.error(request=req,message="Passwords do not match!")
                        return redirect(redirect_to=reverse_lazy("user_signup"))
                    user=User(name=verified_user.name,email=verified_user.email)
                    user.set_password(password)
                    user.save()
                    verified_user.delete()
                    messages.success(request=req,message="Signed up successfully!")
                    return redirect(redirect_to=reverse_lazy("user_login"))
                # if user is not created
                messages.error(req, "Unable to Signup!")
                return redirect(redirect_to=reverse_lazy("user_signup"))
                
        # if verification token not found
        except Verification.DoesNotExist:
                messages.error(req, "Invalid Url!")
                return redirect(redirect_to=reverse_lazy("user_signup"))

        # if the email is not valid
        except ValidationError:
                messages.error(req, "Invalid email address!")
                return redirect(redirect_to=reverse_lazy("user_signup"))

        except Exception as e:
            messages.error(request=req,message="Something went wrong!")
            return redirect(redirect_to=reverse_lazy("user_signup"))
    

    # to create a session with the user
    def create_session(self,req:HttpRequest)->HttpResponse:
        try:
            email,password=req.POST.get("email"),req.POST.get("password")
            # to authenticate the user with the credentials
            user=authenticate(req,email=email,password=password)
            if not user:
                messages.error(request=req,message="Invalid Email/Password")
                return redirect(redirect_to=reverse_lazy("user_login"))
            login(request=req,user=user)
            messages.success(request=req,message="Logged in successfully")
            return redirect(redirect_to=reverse_lazy("home"))
        except Exception as e:
            messages.error(request=req,message="Something went wrong!")
            return redirect(redirect_to=reverse_lazy("user_login"))
    
    # to update users info
    @method_decorator(login_required(login_url=reverse_lazy("user_login")))
    def update_user(self, req: HttpRequest) -> HttpResponse:
        try:
            form = ProfileUpdateForm(data=req.POST, user_instance=req.user, files=req.FILES)
            
            if form.is_valid():
                # Save form data without committing to the database
                user_instance = req.user
                
                email = form.cleaned_data["email"]
                if User.objects.filter(email=email).exclude(id=req.user.id).exists():
                    messages.error(request=req, message="Email already in use")
                    return redirect(reverse_lazy("user_edit_profile"))

                if form.cleaned_data["contact_no"] and not form.cleaned_data["contact_no"].isdigit():
                    messages.error(request=req, message="Contact number should contain numbers only!")
                    return redirect(reverse_lazy("user_edit_profile"))

                # Handle profile picture upload and store GCS URL in model
                uploaded_file = req.FILES.get('profile_picture')
                if uploaded_file:
                    # Read the file content from the InMemoryUploadedFile
                    file_content = uploaded_file.read()

                    # Upload the file content to GCS directly
                    upload_result = upload_file(file_content, f"profile_pictures/{req.user.id}")
                    gcs_url = upload_result.get("obj").public_url

                    user_instance.profile_picture = gcs_url

                    # Save the updated data to the database
                    user_instance.save()
                messages.success(request=req, message="Profile updated successfully!")
                return redirect(reverse_lazy("user_profile"))

            messages.error(request=req, message="Unable to update profile!")
            return redirect(reverse_lazy("user_edit_profile"))

        except Exception as e:
            messages.error(request=req, message="Internal server error!")
            return redirect(reverse_lazy("user_edit_profile"))


    #  for user profile page   

    # ----------------------------GET-------------------------
    @method_decorator(login_required(login_url=reverse_lazy("user_login")))
    def get(self,req:HttpRequest,id:Any=None)->HttpResponse:
        if "profile/edit" in req.path:
            return self.user_profile_edit(req)

        if "profile" in req.path:
            return self.user_profile(req,id=id)
        
        if "destroy-session" in req.path:
            return self.user_logout(req)
    
    # to logout the user
    def user_logout(self,req:HttpRequest)->HttpResponse:
        try:
            logout(req)
            messages.success(request=req,message="Logged out successfully!")
            return redirect(redirect_to=reverse_lazy("user_login"))
        except Exception as e:
            messages.error(request=req,message="Something went wrong, please try again!")
            return redirect(redirect_to=reverse_lazy("home"))

    
    # to get user profile page
    def user_profile(self,req:HttpRequest,id:Any=None)->HttpResponse:
        # if the user is opening its own profile
        if not id:
            try:
                listings=Listing.objects.filter(user_id=req.user)
                data={}
                for listing in listings:
                    image=ListingImages.objects.filter(item_id=listing).first()
                    image.image=generate_signed_url(image.image)
                    data[listing]=image
                return render(req,"users/profile.html",{"listings":data})
            except Exception as e:
                messages.error(request=req,message="Internal server error!")
                return redirect(redirect_to=reverse_lazy("home"))
        # if the user is opening others profile page
        else:
            try:
                user=User.objects.get(id=id)
                listings=Listing.objects.filter(user_id=user)
                data={}
                for listing in listings:
                    image=ListingImages.objects.filter(item_id=listing).first()
                    image.image=generate_signed_url(image.image)
                    data[listing]=image
                return render(req,"users/profile.html",{"listings":data,"profile_user":user})
            # if user not found
            except User.DoesNotExist:
                messages.error(request=req,message="Unable to show profile, please try again!")
                return redirect(redirect_to=reverse_lazy("home"))
            # if something else goes wrong
            except Exception as e:
                messages.error(request=req,message="Internal server error!")
                return redirect(redirect_to=reverse_lazy("home"))

    # get edit profile page
    def user_profile_edit(self,req:HttpRequest)->HttpResponse:
        try:
            form=ProfileUpdateForm(user_instance=req.user,initial={
            "name": req.user.name,
            "email": req.user.email,
            "contact_no": req.user.contact_no,
        })
            return render(req,"users/edit_profile.html",{"form":form})
        # if something goes wrong
        except Exception as e:
            messages.error(request=req,message="Something went wrong!")
            return redirect(reverse_lazy("user_profile"))
