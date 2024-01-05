import os
from marketmate.settings import BASE_DIR

from typing import Any,Optional,Union
from django.views.generic import TemplateView
from django.http import HttpRequest,HttpResponse, JsonResponse, HttpResponseRedirect as redirect
from django.shortcuts import render
from django.views import View

from django.contrib.auth import authenticate, login,logout
# importing login form
from ..forms import AdminLoginForm

# importing models
from users.models import User
from listings.models import Listing,ListingImages

# importing forms
from users.forms import SignupForm,ProfileUpdateForm
from .forms import CreateUserForm

# importing serializers
from api.serializer import FetchUserSerializer,FetchListingSerializer,FetchListingImagesSerializer

# importing email validator
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError



# importing messages module for flash messages
from django.contrib import messages

from django.urls import reverse_lazy
from functools import wraps

from marketmate.gcs_config import generate_signed_url,upload_file,delete_file

def is_admin(redirect_url):
    def decorator(view_method):
        # to preserve the function identity
        @wraps(view_method)
        def wrapper(self,req:HttpRequest,*args, **kwargs)->HttpResponse:
            if not req.user.is_authenticated:
                messages.error(request=req,message="Login to continue")
                return redirect(redirect_to=reverse_lazy(redirect_url))
            if req.user.is_authenticated and not req.user.is_superuser:
                messages.error(request=req,message="Login as admin to continue")
                return redirect(redirect_to=reverse_lazy(redirect_url))
            
            return view_method(self,req,*args, **kwargs)
        return wrapper
    return decorator

class Authentication:
    def is_ajax(req):
        return req.headers.get('x-requested-with') == 'XMLHttpRequest'



class AdminView(View):
    @is_admin(redirect_url="admin_login_page")
    def get(self,req:HttpRequest)->HttpResponse:
        return render(req,"admin/home.html")    
        


# view for admin login page
class AdminLoginView(View):

    def get(self,req:HttpRequest)->HttpResponse:
        if req.user.is_authenticated and req.user.is_superuser:
            return redirect(redirect_to=reverse_lazy("admin_home"))
        return render(req,"admin/login.html",{"loginForm":AdminLoginForm()})


    def post(self,req:HttpRequest)->HttpResponse:
        try:
            if req.user.is_authenticated:
                logout(request=req)
            email=req.POST["email"]
            password=req.POST["password"]
            user=authenticate(email=email, password=password)
            if not user:
                messages.error(req,message="Invalid Email/Password")
                return redirect(reverse_lazy("admin_login_page"))
            if user and not user.is_superuser:
                messages.error(req,message="Login as admin to continue")
                return redirect(reverse_lazy("admin_login_page"))
            login(request=req,user=user)
            messages.success(request=req,message="Logged in as admin!")
            return redirect(reverse_lazy("admin_home"))
        except Exception as e:
            messages.error(req,message="Internal server error, please try again!")
            return redirect(reverse_lazy("home"))
            

class AdminUsersView(View):

    def is_ajax(self,req):
        return req.headers.get('x-requested-with') == 'XMLHttpRequest'
    

    # ------------------------------GET------------------------------------
    
    @is_admin(redirect_url="admin_login_page")
    def get(self,req,id:Any=None)->Union[JsonResponse,HttpResponse]:
        if "admin/users/fetch/" in req.path and not id:
            if Authentication.is_ajax(req):
                return self.get_users_xhr(req)
            return redirect(redirect_to=reverse_lazy("404_not_found"))
        
            

        if "admin/users/create/" in req.path and not id:
            return render(req,template_name="admin/create_user.html",context={"createUserForm":CreateUserForm()})
        
        if "admin/users/destroy/" in req.path and id:
            if self.is_ajax(req):
                return self.delete_user_xhr(req,id)
            return self.delete_user(req,id)

        if "admin/users/" and "/edit/" in req.path and id:
            return self.edit_user_page(req,id)
        if "admin/users/" in req.path and id:
            return self.get_user_page(req,id)

        
    

    def get_users_xhr(self,req)->JsonResponse:
        try:
            users=User.objects.all()
            serializer=FetchUserSerializer(users,many=True)
            return JsonResponse({"users":serializer.data,"message":"Users fetched successfully!"},status=200)
        except Exception as e:
            return JsonResponse({"message":"Internal server error!"},status=500)
    
    def get_user_page(self,req:HttpRequest,id:Any)->HttpResponse:
        try:
            user=User.objects.get(id=id)
            if user.profile_picture:
                user.profile_picture=generate_signed_url(user.profile_picture,True)
            listings=Listing.objects.filter(user_id=user)
            data={}
            for listing in listings:
                image=ListingImages.objects.filter(item_id=listing).first()
                image.image=generate_signed_url(image.image)
                data[listing]=image
            return render(request=req,template_name="admin/user.html",context={"user":user,"listings":data})


        except User.DoesNotExist:
            messages.error(request=req,message="User not found!")
            return redirect(redirect_to=reverse_lazy("admin_home"))  
          
        except Exception as e:
            messages.error(request=req,message="Internal server error!")
            return redirect(redirect_to=reverse_lazy("admin_home"))
    
    def delete_user_xhr(self,req,id:Any)->JsonResponse:
        try:
            user=User.objects.get(id=id)
            self.delete_listings(user)
            user.delete()
            return JsonResponse({"id":user.id,"message":"User deleted successfully!"})
        except User.DoesNotExist:
            return JsonResponse({"message":"User does not exist"},status=404)
        except Exception as e:
            return JsonResponse({"message":"Internal Server error"},status=500)
    
    def delete_user(self,req:HttpRequest,id:Any)->HttpResponse:
        try:
            user=User.objects.get(id=id)
            self.delete_listings(user)
            user.delete()
            messages.success(req,message="User deleted successfully!")
            return redirect(redirect_to=reverse_lazy("admin_home"))
        except User.DoesNotExist:
            messages.error(req,message="User not found!")
            return redirect(redirect_to=reverse_lazy("admin_home"))

        except Exception as e:
            messages.error(req,message="Internal server error!")
            return redirect(redirect_to=reverse_lazy("admin_home"))
    
    def delete_listings(self,user:User)->bool:
        try:
            listings=Listing.objects.filter(user_id=user)
            for listing in listings:
                images=ListingImages.objects.filter(item_id=listing)
                for image in images:
                    delete_file(image.image)
                    image.delete()
                listing.delete()
            return True
        except:
            return False
            
    def edit_user_page(self,req:HttpRequest,id:Any)->HttpResponse:
        try:
            user=User.objects.get(id=id)
            form=ProfileUpdateForm(user_instance=user,initial={
                "name": user.name,
                "email": user.email,
                "contact_no": user.contact_no,
            })
            if user.profile_picture:
                user.profile_picture=generate_signed_url(user.profile_picture,True)
            return render(req,"admin/edit_user.html",{"form":form, "user":user})
        except User.DoesNotExist:
            messages.error(request=req,message="User not found!")
            return redirect(redirect_to=reverse_lazy("admin_home"))
        except Exception as e:
            messages.error(request=req,message="Internal server error!")
            return redirect(redirect_to=reverse_lazy("admin_home"))


        


    # ---------------------------POST--------------------------------
    @is_admin(redirect_url="admin_login_page")
    def post(self,req:HttpRequest,id:Any=None)->HttpResponse:
        if "admin/users/create" in req.path:
            return self.create_user(req=req)
        if "admin/users" and "update/" in req.path and id:
            return self.update_user_profile(req,id)
    def create_user(self,req:HttpRequest)->HttpResponse:
        try:
            form=CreateUserForm(data=req.POST)
            if form.is_valid():

                name=form.cleaned_data["name"]
                email=form.cleaned_data["email"]
                password=form.cleaned_data["password"]
                confirm_password=form.cleaned_data["confirm_password"]

                email_validator=EmailValidator()
                email_validator(email)

                # checking if the user already exists in the database or not
                _user=User.objects.filter(email=email).first()
                # if the user already exists
                if _user:
                    messages.error(request=req,message=f"Email already registered with {_user.name}")
                    return redirect(reverse_lazy("admin_create_user"))
                
                # if not, creating new user
                if password!=confirm_password:
                    messages.error(request=req,message="Passwords do not match!")
                    return redirect(reverse_lazy("admin_create_user"))

                user=User(name=name,email=email)
                user.set_password(password)
                user.save()
                messages.success(request=req,message="new user created  successfully!")
                return redirect(reverse_lazy("admin_home"))
            
            
            messages.error(req, "Unable to create new user!")
            return redirect(reverse_lazy("admin_create_user"))

        except ValidationError:
                messages.error(req, "Invalid email address!")
                return redirect(reverse_lazy("admin_create_user"))

        except Exception as e:
            messages.error(request=req,message="Internal server error!")
            return redirect(reverse_lazy("admin_home"))
        
    def update_user_profile(self,req:HttpRequest,id:Any)->HttpResponse:
        try:
            user=User.objects.get(id=id)
            form=ProfileUpdateForm(data=req.POST,user_instance=user,files=req.FILES)
            if form.is_valid():
                email=form.cleaned_data["email"]
                _user=User.objects.filter(email=email).exclude(id=id).first()
                if _user:
                    messages.error(req,message=f"Email already registered with {_user.name}")
                    # return redirect(redirect_to=reverse_lazy("admin_user_edit_page"))
                    return redirect(redirect_to=reverse_lazy("admin_user_edit_page",kwargs={"id":id}))
                if form.cleaned_data["contact_no"] and not form.cleaned_data["contact_no"].isdigit():
                    messages.error(request=req,message="Contact number should contain numbers only!")
                    return redirect(redirect_to=reverse_lazy("admin_user_edit_page",kwargs={"id":id}))
                # Handle profile picture upload and store GCS URL in model
                uploaded_file = req.FILES.get('profile_picture')
                if uploaded_file:
                    # Read the file content from the InMemoryUploadedFile
                    file_content = uploaded_file.read()

                    # Upload the file content to GCS directly
                    upload_result = upload_file(file_content, f"profile_pictures/{req.user.id}")
                    gcs_url = upload_result.get("obj").public_url
                    user.profile_picture = gcs_url

                    # Save the updated data to the database
                    user.save()
                form.save()
                messages.success(request=req,message="Profile updated successfully!")
                return redirect(redirect_to=reverse_lazy("admin_user_edit_page",kwargs={"id":id}))
                # return redirect(redirect_to=reverse_lazy("admin_home"))
            messages.error(request=req,message="Unable to Update profile!")
            return redirect(redirect_to=reverse_lazy("admin_user_edit_page",kwargs={"id":id}))
            # return redirect(redirect_to=reverse_lazy("admin_user_edit_page"))
        except User.DoesNotExist:
            messages.error(req,message="User not found")
        except Exception as e:
            messages.error(request=req,message="Internal server error!")
            return redirect(redirect_to=reverse_lazy("admin_user_edit_page",kwargs={"id":id}))
            # return redirect(redirect_to=reverse_lazy("user_edit_profile"))


class AdminListingsView(View):
    @is_admin(redirect_url="admin_login_page")
    def get(self,req:HttpRequest,id:Any=None)->Union[JsonResponse,HttpResponse]:
        if "admin/listings/fetch" in req.path and not id:
            if Authentication.is_ajax(req):
                return self.fetch_listings_xhr(req)
        if "admin/listings/destroy" in req.path and id:
            if Authentication.is_ajax(req):
                return self.delete_listing_xhr(req,id)
            return self.delete_listing(req,id)
            
        return redirect(reverse_lazy("404_not_found"))
    
    def fetch_listings_xhr(self,req):
        try:
            listings=Listing.objects.all();
            data=[]
            for listing in listings:
                listing_serializer=FetchListingSerializer(listing)
                listing=listing_serializer.data
                data.append(listing)
            return JsonResponse({"data":data,"messages":"Listings Fetched Successfully!"}, status=200)
        
        except Exception as e:
            return JsonResponse({"messages":"Internal server error!"}, status=500)
        
    def delete_listing_xhr(self,req,id:Any)->JsonResponse:
        try:
            listing=Listing.objects.get(id=id)
            images=ListingImages.objects.filter(item_id=listing)
            for image in images:
                delete_file(image.image)
                image.delete()
            listing.delete()
            return JsonResponse({"id":listing.id,"message":"Listing deleted successfully!"})
        except Listing.DoesNotExist:
            return JsonResponse({"message":"Listing not found"},status=404)
        except Exception as e:
            return JsonResponse({"message":"Internal Server error"},status=404)        


    def delete_listing(self,req:HttpRequest,id:Any)->HttpResponse:
        try:
            listing=Listing.objects.get(id=id)
            images=ListingImages.objects.filter(item_id=listing)
            for image in images:
                delete_file(image.image)
                image.delete()
            listing.delete()
            # return JsonResponse({"id":listing.id,"message":"Listing deleted successfully!"})
            messages.success(request=req,message="Item deleted successfully!")
            return redirect(redirect_to=reverse_lazy("admin_user_page",kwargs={"id":listing.user_id}))
        except Listing.DoesNotExist:
            # return JsonResponse({"message":"Listing not found"},status=404)
            messages.success(request=req,message="Item not found!")
            return redirect(redirect_to=reverse_lazy("admin_user_page",kwargs={"id":listing.user_id}))
        except Exception as e:
            messages.error(request=req,message="Internal server error!")
            return redirect(redirect_to=reverse_lazy("admin_user_page",kwargs={"id":listing.user_id}))

