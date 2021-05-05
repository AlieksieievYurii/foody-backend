from django.contrib import admin
from django.urls import path, include

from users.views import AuthToken

urlpatterns = [
    path('api-token-auth/', AuthToken.as_view(), name='api_token_auth'),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),
]
