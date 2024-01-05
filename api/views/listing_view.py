# importing typing module
from typing import Any
import time,uuid

# importing os and settings
from marketmate.settings import BASE_DIR
import os

# importing API view
from rest_framework.views import APIView

# importing request, response and status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

# for JWT authentication
from ..jwt_authetication import authenticate_jwt


# importing models
from django.db.models import Q
from listings.models import Listing,ListingImages
from users.models import User


from marketmate.gcs_config import generate_signed_url,upload_file

# importing serializers
from ..serializer import (FetchListingSerializer,FetchListingImagesSerializer,CreateListingSerializer,
                          FetchUserSerializer,UpdateListingSerializer)

# importing pagination from rest framework
from rest_framework.pagination import PageNumberPagination

# to generate a unique id against each item
def generate_unique_id():
    id= f"{time.time()}-{uuid.uuid4()}"
    return id[:20]

# listing Api view
class ListingApiView(APIView,PageNumberPagination):
    # declaring page size for pagination
    page_size=10

    # ---------------------------GET------------------------
    def get(self, req:Request,user:Any=None,id:Any=None)->Response:
        get_all=req.GET.get("all")
        paginated=req.GET.get("paginated")
        
        query=req.GET.get("query")
        if "/search/" in req.path:
            return self.search(req=req,query=query)
        if "/filter/" in req.path:
            return self.filter(req=req,query=query)
        if get_all and get_all=="True":
            return self.fetch_all_items(req=req)
        if paginated and paginated=="True":
            return self.fetch_items_paginated(req)
        if user:
            return self.fetch_items(req=req,user=user)
        if id:
            return self.fetch_one(req=req,id=id)

        # if the url is not recognized
        return Response({"message":["Invalid request"]},status=status.HTTP_400_BAD_REQUEST)

    # to search items from listing
    def search(self,req:Request,query:str=None)->Response:
        try:
            if not query:
                return Response({"messages":["Invalid query!"]},status=status.HTTP_400_BAD_REQUEST)

            data=[]
            # to filter the items in the basis of title or description
            listings=Listing.objects.filter(Q(title__icontains=query)|Q(title__icontains=query))

            for listing in listings:
                listing_serializer=FetchListingSerializer(listing)
                images=ListingImages.objects.filter(item_id=listing)
                listing_images_serializer=FetchListingImagesSerializer(images,many=True)
                listing=listing_serializer.data
                listing_images=listing_images_serializer.data
                for image in listing_images:
                    image["image"]=generate_signed_url(image["image"])
                listing["images"] = listing_images
                data.append(listing)

            return Response({"data":data,"messages":["Listings fetched successfully!"]},status=status.HTTP_200_OK)
            # if something goes wrong
        except Exception as e:
            return Response({"messages":["Internal Server error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # to filter items from listing, on basis of category    
    def filter(self,req:Request,query:str=None)->Response:
        try:
            # if no query is passed
            if not query:
                return Response({"messages":["Invalid query!"]},status=status.HTTP_400_BAD_REQUEST)
            data=[]
            listings=Listing.objects.filter(category__iexact=query)
            for listing in listings:
                listing_serializer=FetchListingSerializer(listing)
                images=ListingImages.objects.filter(item_id=listing)
                listing_images_serializer=FetchListingImagesSerializer(images,many=True)
                listing=listing_serializer.data
                listing_images=listing_images_serializer.data
                for image in listing_images:
                    image["image"]=generate_signed_url(image["image"])
                listing["images"] = listing_images
                data.append(listing)

                
            return Response({"data":data,"messages":["Listings fetched successfully!"]},status=status.HTTP_200_OK)
            # if something goes wrong
        except Exception as e:
            return Response({"messages":["Internal Server error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

    # to fetch a single item on the basis of the id provided
    def fetch_one(self,req:Request,id:Any)->Response:
        try:
            listing=Listing.objects.get(id=id)
            listing_serializer=FetchListingSerializer(listing)
            images_serializer=FetchListingImagesSerializer(ListingImages.objects.filter(item_id=listing),many=True)
            user_serializer=FetchUserSerializer(User.objects.get(id=listing.user_id))
            data=listing_serializer.data
            data["created by"]=user_serializer.data
            images_data=images_serializer.data
            for image in images_data:
                image["image"]=generate_signed_url(image["image"])
            data["images"]=images_serializer.data
            return Response({"data":data},status=status.HTTP_200_OK)
        # if the item is ont found
        except Listing.DoesNotExist:
            return Response({"messages":["Listing not found!"]},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"messages":["Internal Server Error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # to fetch the listings according to a user
    def fetch_items(self,req:Request,user:Any)->Response:
    # to get all the items posted by a specific user
        try:
            # to get the listings, according ti user id
            items = Listing.objects.filter(user_id=user)
            if not items:
                return Response({"messages":["User and Listings not found!"]},status=status.HTTP_404_NOT_FOUND)

            data = []
            for item in items:
                images = ListingImages.objects.filter(item_id=item)
                item_serializer = FetchListingSerializer(item)
                images_serializer = FetchListingImagesSerializer(images, many=True)
                item_data = item_serializer.data
                listing_images=images_serializer.data
                for image in listing_images:
                    image["image"]=generate_signed_url(image["image"])
                item_data = item_serializer.data
                item_data["images"] = listing_images
                data.append(item_data)
            return Response({"data":data,"messages":["Items Fetched Successfully!"]},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"messages":["INternal server error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # to fetch all the items from the DB
    def fetch_all_items(self,req:Request)->Response:
        try:
            items=Listing.objects.all()
            data=[]
            for item in items:
                images = ListingImages.objects.filter(item_id=item)
                item_serializer = FetchListingSerializer(item)
                images_serializer = FetchListingImagesSerializer(images, many=True)
                listing_images=images_serializer.data
                for image in listing_images:
                    image["image"]=generate_signed_url(image["image"])
                item_data = item_serializer.data
                item_data["images"] = listing_images
                data.append(item_data)
            return Response({"data":data,"messages":["Items Fetched Successfully!"]},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"messages":["Internal server error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # to fetch all the items paginated with size 10
    def fetch_items_paginated(self,req:Request)->Response:
        try:
            items=Listing.objects.all()
            paginated_items=self.paginate_queryset(items,request=req)

            data=[]
            for item in paginated_items:
                images = ListingImages.objects.filter(item_id=item)
                item_serializer = FetchListingSerializer(item)
                images_serializer = FetchListingImagesSerializer(images, many=True)

                item_data = item_serializer.data
                listing_images=images_serializer.data
                for image in listing_images:
                    image["image"]=generate_signed_url(image["image"])
                item_data = item_serializer.data
                item_data["images"] = listing_images
                data.append(item_data)
            return Response({"data":data,"messages":["Items Fetched Successfully!"]},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"messages":["Internal server error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------------POST------------------------
    # to create new item
    @authenticate_jwt # using decorator for authentication and authorization
    def post(self,req:Request)->Response:
        try:
            serializer=CreateListingSerializer(data=req.data)
            # if the serializer is valid
            if serializer.is_valid():
                data=serializer.validated_data
                listing = Listing(title=data['title'], category=data['category'], user=req.user)
                if "price" in data:
                    listing.price=data["price"]
                if "description" in data:
                    listing.description=data["description"]
                    # to save the new item 
                listing.save()

                images=data.get("images") or []
                for image in images:
                    file_content = image.read()

                    upload_result = upload_file(file_content, f"listings/{generate_unique_id()}")
                    gcs_url = upload_result.get("obj").public_url 
                    ListingImages(image=gcs_url,item=listing).save()
                return Response({"messages": ["Listing created successfully!"]}, status=status.HTTP_201_CREATED)

            return Response({"messages": ["Invalid data"]}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"messages": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ---------------------PATCH-----------------------
    # to update the item
    @authenticate_jwt # using decorator for authentication and authorization
    def patch(self,req:Request,id:Any)->Response:
        try:
            if not id:
                return Response({"messages":["Invalid request, provide id"]},status=status.HTTP_400_BAD_REQUEST)
            listing=Listing.objects.get(id=id)
            # if user is not admin, or the user isn't the creator of the item
            if not req.user.is_superuser and listing.user_id!=req.user.id :
                return Response({"messages":["Unauthorized"]},status=status.HTTP_401_UNAUTHORIZED)
                
            serializer=UpdateListingSerializer(data=req.data)
            if serializer.is_valid():
                data=serializer.validated_data
                if "title" in data:
                    listing.title=data["title"]
                if "description" in data:
                    listing.description=data["description"]
                if "price" in data:
                    listing.price=data["price"]
                if "category" in data:
                    listing.category=data["category"]
                listing.save()
                deserialized_data=FetchListingSerializer(listing)
                return Response({"data":deserialized_data.data,"messages":["Listing item updated successfully!"]})

            return Response({"messages":["Invalid data"]},status=status.HTTP_400_BAD_REQUEST)


        # if the item to be updated is not found
        except Listing.DoesNotExist:
            return Response({"messages":["Listing item does not exist"]},status=status.HTTP_404_NOT_FOUND)

            # if something goes wrong
        except Exception as e:
            return Response({"messages":["Internal server error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            



    # ---------------------DELETE----------------------
    # to delete a item form the DB and server
    def delete(self,req:Request,id:Any)->Response:
        try:
            # if no id is provided
            if not id:
                return Response({"messages":["Invalid request, provide id"]},status=status.HTTP_400_BAD_REQUEST)
            listing=Listing.objects.get(id=id)
            
            # to get the images associated with the listing from the database
            images=ListingImages.objects.filter(item_id=id)
            # to delete the image files from the server
            for image in images:
                image_path=os.path.join(BASE_DIR,image.image)
                if os.path.exists(image_path):
                    os.remove(image_path)
                image.delete()
            listing.delete()
            return Response({"messages":["Listing item deleted successfully!"]},status=status.HTTP_200_OK)
        # if the listing item with the id not found
        except Listing.DoesNotExist:
            return Response({"messages":["Listing item not found!"]},status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"messages":["Internal server error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
