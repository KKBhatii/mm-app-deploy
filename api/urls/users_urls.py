from django.urls import path

# importing User Ap view
from ..views.users_view import UserApiView


urlpatterns = [
    path("fetch/",UserApiView.as_view()),
    path("fetch/<id>",UserApiView.as_view()),
    path("create/",UserApiView.as_view()),
    path("auth/generate-token/",UserApiView.as_view()),
    path("<id>/update/",UserApiView.as_view()),
    path("update/",UserApiView.as_view()),
    path("destroy/",UserApiView.as_view()),
    path("destroy/<id>",UserApiView.as_view()),
]