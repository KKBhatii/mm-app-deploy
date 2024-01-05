from django.urls import path

from .views import AdminView,AdminLoginView,AdminUsersView,AdminListingsView




urlpatterns = [

    #USERS
    path('', AdminView.as_view(), name="admin_home"),
    path('login/', AdminLoginView.as_view(), name="admin_login_page"),
    path('login/create-session/', AdminLoginView.as_view(), name="admin_login"),
    path('users/fetch/', AdminUsersView.as_view(), name="admin_get_users_xhr"),
    path('users/<id>', AdminUsersView.as_view(), name="admin_user_page"),
    path('users/<id>/edit/', AdminUsersView.as_view(), name="admin_user_edit_page"),
    path('users/<id>/update/', AdminUsersView.as_view(), name="admin_update_user"),
    path('users/create/', AdminUsersView.as_view(), name="admin_create_user"),
    path('users/destroy/<id>', AdminUsersView.as_view(), name="admin_delete_user"),

    # LISTINGS
    path('listings/fetch/', AdminListingsView.as_view(), name="admin_get_listing_xhr"),
    path('listings/destroy/<id>', AdminListingsView.as_view(), name="admin_delete_listing"),
]