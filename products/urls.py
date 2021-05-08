from rest_framework import routers

from products.views import ProductView, ProductImageView

router = routers.SimpleRouter()
router.register('images', ProductImageView)
router.register('', ProductView)
urlpatterns = router.urls
