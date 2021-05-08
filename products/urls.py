from django.urls import path
from rest_framework import routers

from products.views import ProductView, ProductImageView, ImageUploadView, AvailabilityView, CategoryView, \
    ProductCategoryView

router = routers.SimpleRouter()
router.register('images', ProductImageView)
router.register('availabilities', AvailabilityView)
router.register('categories', CategoryView)
router.register('productCategory', ProductCategoryView)
router.register('', ProductView)
urlpatterns = [
                  path('images/upload/', ImageUploadView.as_view())
              ] + router.urls
