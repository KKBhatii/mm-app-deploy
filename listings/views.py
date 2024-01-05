#importing time and uuid
import uuid,time

# importing typing
from typing import Any
# importing django modules
from django.http import HttpRequest,HttpResponse, JsonResponse, HttpResponseRedirect as redirect
from django.shortcuts import render
from django.urls import reverse_lazy

# miporting is and BASE dir URI form settings
import os
from marketmate.settings import BASE_DIR

# impoting django views
from django.views.generic import TemplateView
from django.views import View

# importing forms
from .forms import ListItemForm

# importing decorators
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# importing models
from .models import Listing,ListingImages
from users.models import User

# importing serializer
from api.serializer import FetchListingImagesSerializer

# importing authentication
from marketmate.admin.views import Authentication

# importing mailers
from marketmate.mailer import send_notification_mail

# importing messages module for flash messages
from django.contrib import messages

from marketmate.gcs_config import upload_file,generate_signed_url,delete_file

# to render the sell item page
class ListItemView(TemplateView):
    template_name="listings/list_item.html"
    @method_decorator(login_required(login_url="/users/login/"))
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs:Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = ListItemForm()
        return context

# to generate a unique id against each item
def generate_unique_id():
    id= f"{time.time()}-{uuid.uuid4()}"
    return id[:20]

# listing view
class ListingView(View):

    # ------------------------------------POST--------------------------------
    # to handle post requests
    @method_decorator(login_required(login_url=reverse_lazy("user_login")))
    def post(self,req:HttpRequest)->HttpResponse:
        if "list-item/create" in req.path:
            return self.create_item(req=req)

    # to list new item
    def create_item(self,req:HttpRequest)->HttpResponse:
        try: 
            form=ListItemForm(data=req.POST, files=req.FILES)
            # if form data is valid
            if form.is_valid():
                title=form.cleaned_data["title"]
                description=form.cleaned_data["description"]
                category=form.cleaned_data["category"]
                price=form.cleaned_data["price"]
                images=req.FILES.getlist("images")
                if len(images)<1:
                    messages.error(request=req,message="PLease select at least one IMAGE !")
                    return redirect(redirect_to=reverse_lazy("home"))

                listing=Listing(title=title,description=description,category=category,user=req.user,price=price)
                listing.save()

                for image in images:
                    file_content = image.read()
                    upload_result = upload_file(file_content, f"listings/{generate_unique_id()}")
                    gcs_url = upload_result.get("obj").public_url 
                    ListingImages(image=gcs_url,item=listing).save()
                
                messages.success(request=req,message="Product listed successfully!")
                return redirect(redirect_to=reverse_lazy("user_profile"))
            
            # to show the relevant error message to the user
            if form.errors:
                for key,val in form.errors.items():
                    if "category" in key.lower():
                        messages.error(req,"Please select a category")
                    elif "title" in key.lower():
                        messages.error(req,"Please provide a title")
                    elif "images" in key.lower():
                        messages.error(request=req,message=val[0])
                    elif "price" in key.lower():
                        messages.error(request=req,message=val[0])
                    else:
                        messages.error(request=req,message="Unable to list your product!")
            else:
                messages.error(request=req,message="Unable to list your product!")
            return redirect(redirect_to=reverse_lazy('listing_list_item'))

        except Exception as e:
            print(e)
            messages.error(request=req,message="Internal server error!")
            return redirect(redirect_to=reverse_lazy('listing_list_item'))

    # -----------------------------GET---------------------------------
    

    def get(self,req:HttpRequest,id:Any=None)->HttpResponse:
        if "fetch" in req.path:
            if Authentication.is_ajax(req=req) and id:
                return self.get_images_xhr(req,id)
            if id:
                return self.fetch_one(req,id=id)
            else:
                messages.error(req,message="Item not found")
                return redirect(redirect_to=reverse_lazy("home"))
        if "destroy" in req.path and id:
            return self.destroy_item(req,id=id)
        if "notify-user/mail" in req.path and id:
            return self.mail_user(req,id)
        
        return redirect(redirect_to=reverse_lazy("404_not_found"))
    
    # to fetch an item to the given id
    def fetch_one(self,req:HttpRequest,id:Any)->HttpResponse:
        try:
            item=Listing.objects.get(id=id)
            user=User.objects.filter(id=item.user_id).first()
            return render(req,"listings/item_page.html",{"data":{"item":item,"listed_by":user}})
            # if the listing is not found
        except Listing.DoesNotExist:
            messages.error(request=req,message="Item not found or deleted!")
            return redirect(redirect_to=reverse_lazy("home"))

        except Exception as e:

            messages.error(request=req,message="Internal server error!")
            return redirect(redirect_to=reverse_lazy("home"))
    
    # to get the images with an xhr request
    def get_images_xhr(self,req,id)->JsonResponse:
        try:
            listing_images= ListingImages.objects.filter(item_id=id)
            images_serializer=FetchListingImagesSerializer(listing_images,many=True)
            images_data=images_serializer.data
            for image_data in images_data:
                image_data["image"]=generate_signed_url(image_data["image"])
            return JsonResponse({"images":images_data,"message":"Images fetched successfully!"},status=200)
        except Exception as e:
            return JsonResponse({"message":"Internal server error!"},status=500)

    
    # to delete the item
    @method_decorator(login_required(login_url=reverse_lazy("user_login")))
    def destroy_item(self, req:HttpRequest, id:Any)->HttpResponse:
        try:
            listing=Listing.objects.get(id=id)
            if listing.user_id!=req.user.id:
                messages.error(request=req,message="Unauthorized to delete this item!")
                return redirect(redirect_to=reverse_lazy("home"))
            images=ListingImages.objects.filter(item_id=listing)
            # to delete the images from the disk 
            for image in images:
                delete_file(image.image)
                image.delete()
            listing.delete()
            messages.success(req,message="Item deleted successfully!")
            return redirect(redirect_to=reverse_lazy("user_profile"))
            # if listing not found
        except Listing.DoesNotExist:
            messages.error(req,message="Item does not exist!")    
            return redirect(redirect_to=reverse_lazy("user_profile"))

        except Exception as e:
            messages.error(req,message="Internal server error!")
            return redirect(redirect_to=reverse_lazy("user_profile"))

    # to mail the user, if someone is interested in their product
    def mail_user(self,req,id)->JsonResponse:
        try:
            listing=Listing.objects.get(id=id)
            user=User.objects.get(id=listing.user_id)
            # if user is logged in
            if not req.user.is_authenticated:
                return JsonResponse({"message":"Please login to continue!"}, status=403)
            item_url=f"{req.build_absolute_uri('/')}listings/fetch/{id}"
            if send_notification_mail(send_to=user.email,user=req.user,item_url=item_url,recipient=user.name):
                return JsonResponse({"message":f"Mail sent to {user.name} !"}, status=200)
            return JsonResponse({"message":f"Unable to send mail, please try again !"}, status=400)
            # if listing not found
        except Listing.DoesNotExist:
            return JsonResponse({"message":"Listed item does not exist or deleted!"}, status=404)
            # if user not found
        except User.DoesNotExist:
            return JsonResponse({"message":"User not found!"}, status=404)
        except Exception as e:
            return JsonResponse({"message":"Internal server error!"}, status=500)
    
