
from django.urls import path,include
from django.conf.urls.static import static

# importing upload url from settings
from .settings import DEBUG,UPLOAD_ROOT,UPLOAD_URL

# importing urls
import listings.urls as listings_urls
import users.urls as users_urls
import api.urls.urls as api_urls
from .admin import urls as admin_urls

# importing view for resource not found
from .views import ResourceNotFoundView

# importing Home view
from .views import Home

urlpatterns = [
    path('admin/', include(admin_urls)),
    path('', Home.as_view(),name="home"),
    path('users/', include(users_urls)),
    path("listings/", include(listings_urls)),
    path("api/", include(api_urls)),
    path("404/",ResourceNotFoundView.as_view() ,name="404_not_found"),

]

# making static path available for the browser
if DEBUG:
    urlpatterns+= static(UPLOAD_URL,document_root=UPLOAD_ROOT)
