from django.urls import path, include

# importing urls
from .users_urls import urlpatterns as users_urls
from .listings_urls import urlpatterns as listing_urls

urlpatterns = [
    path("users/", include(users_urls)),
    path("listings/", include(listing_urls)),
]
