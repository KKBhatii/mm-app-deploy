from django.urls import path

# importing my view
from .views import SignUpView,LoginView, UserView,CreateUserView
from marketmate.views import ResourceNotFoundView

urlpatterns = [
    path("sign-up/", SignUpView.as_view(),name="user_signup"),
    path("login/", LoginView.as_view(),name="user_login"),
    path("create/", UserView.as_view(),name="user_create"),
    path("create/<token>", UserView.as_view(),name="user_create_verify"),
    path("verify/<token>", CreateUserView.as_view(),name=""),
    path("create-session/", UserView.as_view(),name="user_create_session"),
    path("destroy-session/", UserView.as_view(),name="user_destroy_session"),
    path("profile/", UserView.as_view(),name="user_profile"),
    path("<id>/profile/", UserView.as_view(),name="user_other_profile"),
    path("profile/edit/", UserView.as_view(),name="user_edit_profile"),
    path("profile/update", UserView.as_view(),name="user_update_profile"),

    # for every path other than specified
    path("<path:unknown_path>", (ResourceNotFoundView.as_view()),name="unknown_path"),
]
