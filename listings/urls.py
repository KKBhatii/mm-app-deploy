from django.urls import path

# importing the views
from .views import ListItemView,ListingView
urlpatterns=[
    path("list-item/",ListItemView.as_view(),name="listing_list_item"),
    path("list-item/create/",ListingView.as_view(),name="listing_create_item"),
    path("fetch/<id>",ListingView.as_view(),name="listing_fetch_one"),
    path("fetch/",ListingView.as_view(),name="listing_fetch_one"),
    path("destroy/<id>",ListingView.as_view(),name="listing_delete_item"),
    path("<id>/notify-user/mail/",ListingView.as_view(),name="")
]


    