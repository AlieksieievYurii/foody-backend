from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]
