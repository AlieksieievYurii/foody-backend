from django.urls import path
from rest_framework import routers

from products.views import ProductView, ProductImageView, ImageUploadView, AvailabilityView, CategoryView

router = routers.SimpleRouter()
router.register('images', ProductImageView)
router.register('availabilities', AvailabilityView)
router.register('categories', CategoryView)
router.register('', ProductView)
urlpatterns = [
                  path('images/upload/', ImageUploadView.as_view())
              ] + router.urls
