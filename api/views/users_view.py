# importing typing
from typing import Any,List
# importing os and settings
import os
from marketmate.settings import BASE_DIR

# importing API view
from rest_framework.views import APIView

# importing request, response and status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

import os
from marketmate.settings import BASE_DIR

from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import AccessToken

# importing model
from users.models import User
from listings.models import Listing,ListingImages

# importing serializers
from ..serializer import (UserRegistrationSerializer,GenerateTokenSerializer,
                          UpdateProfileSerializer)
from ..serializer import FetchListingSerializer,FetchListingImagesSerializer,FetchUserSerializer

# for JWT authentication
from ..jwt_authetication import authenticate_jwt

from marketmate.gcs_config import generate_signed_url,upload_file,delete_file

class UserApiView(APIView):
    # --------------GET------------------
    # to fetch all the users
    # only for admin
    @authenticate_jwt
    def get(self,req:Request, id:Any=None)->Response:
        try:
            # if the user is not the admin
            if not req.user.is_superuser:
                return Response({"messages":["Unauthorized!"]},status=status.HTTP_401_UNAUTHORIZED) 
            query=req.GET.get("listings")
            # if the users to be fetched with the listings
            if query and query=="True":
                return self.get_with_listings(req=req,id=id)
            return self.get_users_without_listings(req)


        except Exception:
            return Response({"message":["Internal Server error "]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # to fetch all the users with the listings 
    def get_with_listings(self,req:Request,id:Any=None)->Response:
        try:
            data=[]
            users=User.objects.all()
            # if no user found
            if not users:
                return Response({"data":data,"message":["No user found!"]},status=status.HTTP_404_NOT_FOUND)

            # to map the listing item with the users
            for user in users:
                user_serializer=FetchUserSerializer(user)
                user_data=user_serializer.data
                if user_data["profile_picture"]:
                    user_data["profile_picture"]=generate_signed_url(user_data["profile_picture"])
                user_data["listings"]=self.get_listings(user)
                data.append(user_data)
            
            return Response({"data":data,"message":["Users with listings fetched successfully "]},status=status.HTTP_200_OK)
            

        except Exception as e:
            return Response({"message":["Internal Server error "]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # to fetch the listings from the database associated with a user
    def get_listings(self,user:User)->List[dict]:
        listings=[]
        items=Listing.objects.filter(user_id=user)
        for item in items:
            images=ListingImages.objects.filter(item_id=item)
            item_serializer=FetchListingSerializer(item)
            images_serializer=FetchListingImagesSerializer(images,many=True)
            item_data=item_serializer.data
            item_images=images_serializer.data
            for image in item_images:
                image["image"]=generate_signed_url(image["image"])

            item_data["images"]=images_serializer.data
            listings.append(item_data)
        
        return listings
    

    # to get all the users without the listings
    def get_users_without_listings(self,req:Request)->Response:
        try:
            users=User.objects.all()
            # if no user found
            if not users:
                return Response({"message":["No user found!"]},status=status.HTTP_404_NOT_FOUND)
            
            serialized_user=FetchUserSerializer(users,many=True)
            users_data=serialized_user.data
            if users_data["profile_picture"]:
                users_data["profile_picture"]=generate_signed_url(users_data["profile_picture"])
            return Response({"data":users_data,"message":["Users with listings fetched successfully "]},status=status.HTTP_200_OK)
            

        except Exception as e:
            return Response({"message":["Internal Server error "]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



    # ------------POST------------------
    # to create new user, or to generate authentication token
    def post(self,req:Request)->Response:
        if "create" in req.path:
            return self.create_user(req=req)
        elif "auth/generate-token" in req.path:
            return self.generate_token(req=req)

    # to create new user
    def create_user(self,req:Request)->Response:
        try:
            # to serialize the data
            serializer=UserRegistrationSerializer(data=req.data)
            # if the serialized data is valid
            if serializer.is_valid():
                name=serializer.validated_data["name"]
                email=serializer.validated_data["email"]
                password=serializer.validated_data["password"]
                # checking if the user already exists or not
                user=User.objects.filter(email=email).first()
                # if user exists
                if user:
                    return Response({"messages":["User already exists!"]} ,status=status.HTTP_400_BAD_REQUEST)
                
                # if the user does not exists, creating a new user
                new_user=User(email=email,name=name)
                new_user.set_password(raw_password=password)
                new_user.save()
                # if the user created successfully
                if new_user:
                    return Response({"user":{ "id":new_user.id,"name":new_user.name,"email":new_user.email,}
                                      ,"message":["User created successfully!"]},status=status.HTTP_201_CREATED)
                # if the user isn't created
                return Response({"message":["Unable to create user!"]},status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # if the data isn't valid
            messages=[]
            for key,val in serializer.errors.items():
                if val[0].code.lower()=="required":
                    messages.append(f"{key}, {val[0]}")
                elif val[0].code.lower()=="invalid":
                    messages.append(val[0])
            return Response({"messages":messages},status=status.HTTP_400_BAD_REQUEST)
        
        # if something else went wrong
        except Exception as e:
            return Response({"message":["Internal Server error"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # to generate the authentication token 
    def generate_token(self,req:Request)->Response:
        try:
            serializer=GenerateTokenSerializer(data=req.data)
            if serializer.is_valid():
                email=serializer.validated_data["email"]
                password=serializer.validated_data["password"]
                user=authenticate(email=email,password=password)
                if not user:
                    return Response({"messages":["Incorrect Email/Password"]},status=status.HTTP_401_UNAUTHORIZED)
                token=AccessToken()
                # including user id in the payload
                token["user_id"]=user.id
                return Response({"user":{ "id":user.id,"name":user.name, "email":user.email, },
                    "token":str(token),"messages":["Token generated"]}, status=status.HTTP_200_OK)
            
            messages=[]
            # for errors
            for key,val in serializer.errors.items():
                if val[0].code.lower()=="required":
                    messages.append(f"{key}, {val[0]}")
                elif val[0].code.lower()=="invalid":
                    messages.append(val[0])
            return Response({"messages":messages},status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"message":["Internal Server error"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    # ------------------PATCH-------------
    # to update user details, require authentication
    @authenticate_jwt 
    def patch(self, req:Request,id:Any=None)->Response:
        
        try:
            # if no id is provided, then the user want update its owm info
            if not id or req.user.id==id:
                user=req.user
                serializer=UpdateProfileSerializer(data=req.data)
                if serializer.is_valid():
                    validated_data=serializer.validated_data
                    if "name" in validated_data:
                        user.name=validated_data["name"]
                    if "email" in validated_data:
                        user.email=validated_data["email"]
                    if "profile_picture" in validated_data:
                        user.profile_picture=validated_data["profile_picture"]
                    if "contact_no" in validated_data:
                        user.contact_no=validated_data["contact_no"]
                    
                    user.save()
                    return Response({"user":{"id":user.id,"name":user.name},"messages":["User updated successfully"]},status=status.HTTP_202_ACCEPTED)
                # if there is error in serializer
                if serializer.errors:
                    messages=[]
                    for key, value in serializer.errors.items():
                        messages.append(f"{key}, {value}")
                    return Response({"messages":messages},status=status.HTTP_400_BAD_REQUEST)
                # if there is another issue
                return Response({"messages":["Unable to update user!"]},status=status.HTTP_400_BAD_REQUEST)


            # if there is id, then user wants to update others profile
            # checking user making this request is admin or not
            # if user is not the admin then
            if not req.user.is_superuser:
                return Response({"messages":["Unauthorized!"]},status=status.HTTP_401_UNAUTHORIZED)

            # getting the user by the id
            try:
                user=User.objects.get(id=id)
            # if no user found
            except User.DoesNotExist:
                return Response({"messages":["User not found!"]},status=status.HTTP_400_BAD_REQUEST)


            serializer=UpdateProfileSerializer(data=req.data)
            if serializer.is_valid():
                validated_data=serializer.validated_data
                if "name" in validated_data:
                    user.name=validated_data["name"]
                if "email" in validated_data:
                    user.email=validated_data["email"]
                if "profile_picture" in validated_data:
                    user.profile_picture=validated_data["profile_picture"]
                if "contact_no" in validated_data:
                    user.contact_no=validated_data["contact_no"]
                
                user.save()
                return Response({"user":{"id":user.id,"name":user.name},"messages":["User updated successfully"]},status=status.HTTP_202_ACCEPTED)
                # if there is error in serializer
            if serializer.errors:
                messages=[]
                for key, value in serializer.errors.items():
                    messages.append(f"{key}, {value}")
                return Response({"messages":messages},status=status.HTTP_400_BAD_REQUEST)
                # if there is another issue
            return Response({"messages":["Unable to update user!"]},status=status.HTTP_400_BAD_REQUEST)
                 
        # if the error occurs
        except Exception as e:
            return Response({"messages":["Internal server error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --------------------DELETE---------------
    # to delete the user
    @authenticate_jwt   
    def delete(self,req:Request,id:Any=None)->Response:
        try:
        # if the user wants to delete itself from the platform
            if not id or req.user.id==id:
                user=User.objects.get(id=req.user.id)
            else:
            # if want to delete someone else's data, checking is it admin or not
                if not req.user.is_superuser:
                    return Response({"messages":["Unauthorized!"]},status=status.HTTP_401_UNAUTHORIZED)

                user=User.objects.get(id=id)
            # deleting the profile pic file from the server
            if user.profile_picture:
                if not delete_file(str(user.profile_picture),True):
                    return Response({"messages":["Something went wrong, Unable to delete user!"]},status=status.HTTP_400_BAD_REQUEST)
            if not self.delete_listings(user=user):
                    return Response({"messages":["Something went wrong, Unable to delete user!"]},status=status.HTTP_400_BAD_REQUEST)

            user.delete()
            return Response({"messages":["User deleted successfully!"]},status=status.HTTP_200_OK)
        # if the user is not found
        except User.DoesNotExist:
                return Response({"messages":["User not found!"]},status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"messages":["Internal server error!"]},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # to delete the listings associated to the user, if the user is deleted
    def delete_listings(self,user:User)->bool:
        try:      
            items=Listing.objects.filter(user_id=user)
            for item in items:
                if not self.remove_images(item):
                    return False
                item.delete()
            return True
        except Exception as e:
            return False

    # to remove the images from the server
    def remove_images(self,listing:Listing)->bool:
        try:
            images=ListingImages.objects.filter(item_id=listing)
            for image in images:
                delete_file(image.image)
                image.delete()
            return True
        except Exception as e:
            return False
        