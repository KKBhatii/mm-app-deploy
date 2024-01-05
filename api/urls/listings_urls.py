from django.urls import path

# importing api views
from ..views.listing_view import ListingApiView

urlpatterns = [
    path("fetch/",ListingApiView.as_view()),
    path("<user>/fetch/",ListingApiView.as_view()),
    path("fetch/<id>/",ListingApiView.as_view()),
    path("create/",ListingApiView.as_view()),
    path("update/<id>/",ListingApiView.as_view()),
    path("search/",ListingApiView.as_view()),
    path("filter/",ListingApiView.as_view()),
]