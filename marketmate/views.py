# importing important modules, classes and functions
from typing import Any
from django.http import HttpRequest,HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

# importing models
from listings.models import Listing,ListingImages

# for home view
class Home(View):
    def get(self,req:HttpRequest)->HttpResponse:
        listings=Listing.objects.all()
        data={}
        for listing in listings:
            image=ListingImages.objects.filter(item_id=listing).first()
            data[listing]=image
        return render(req,"home.html",{"data":data})


# to render the resource not found page
class ResourceNotFoundView(TemplateView):
    template_name="404.html"
    
