# importing serializer from rest framework
from rest_framework import serializers


# --------------------USER SERIALIZERS------------------

# serializer to create new user
class UserRegistrationSerializer(serializers.Serializer):
    name=serializers.CharField(max_length=100,required=True)
    email=serializers.EmailField(required=True)
    password=serializers.CharField(max_length=255,required=True)
    confirm_password=serializers.CharField(max_length=255,required=True)

    def validate(self, data):
        if data["password"]!=data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return super().validate(data)

# serializer to generate token
class GenerateTokenSerializer(serializers.Serializer):
    email=serializers.EmailField(required=True)
    password=serializers.CharField(required=True)

# serializer to update user profile
class UpdateProfileSerializer(serializers.Serializer):
    name=serializers.CharField(required=False)
    email=serializers.EmailField(required=False)
    contact_no=serializers.IntegerField(required=False)
    profile_picture=serializers.ImageField(required=False)

# serializer to fetch user
class FetchUserSerializer(serializers.Serializer):
    id=serializers.CharField()
    name=serializers.CharField()
    email=serializers.EmailField()
    contact_no=serializers.IntegerField()
    created_at=serializers.DateTimeField()
    updated_at=serializers.DateTimeField()
    
    
    
# --------------------LISTINGS SERIALIZERS------------------

# serializer to fetch listings
class FetchListingSerializer(serializers.Serializer):
    id=serializers.CharField()
    title=serializers.CharField()
    description=serializers.CharField()
    price=serializers.IntegerField()
    category=serializers.CharField()
    user=serializers.CharField()
    created_at=serializers.DateTimeField()
    updated_at=serializers.DateTimeField()

# serializer to fetch images
class FetchListingImagesSerializer(serializers.Serializer):
    image = serializers.ImageField()

# serializer ti create listing
class CreateListingSerializer(serializers.Serializer):
    title=serializers.CharField()
    description=serializers.CharField(required=False)
    price=serializers.IntegerField(required=False)
    category=serializers.CharField()
    images=serializers.ImageField(required=False)

# serializer ot update listing
class UpdateListingSerializer(serializers.Serializer):
    title=serializers.CharField(required=False)
    description=serializers.CharField(required=False)
    price=serializers.IntegerField(required=False)
    category=serializers.CharField(required=False)
    images=serializers.ImageField(required=False)
    