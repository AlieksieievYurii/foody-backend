from django.urls import path
from rest_framework import routers

from products.views import ProductView, ProductImageView, ImageUploadView

router = routers.SimpleRouter()
router.register('images', ProductImageView)
router.register('', ProductView)
urlpatterns = [
                  path('images/upload/', ImageUploadView.as_view())
              ] + router.urls
