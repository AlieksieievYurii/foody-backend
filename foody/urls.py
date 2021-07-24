from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from users.views import AuthToken

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="REST API of Foody Backend",
        contact=openapi.Contact(email="alieksieiev.yurii@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)

urlpatterns = [
    path('api-token-auth/', AuthToken.as_view(), name='api_token_auth'),
    path('users/', include('users.urls')),
    path('products/', include('products.urls')),
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls')),

    path(r'swagger<str:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
