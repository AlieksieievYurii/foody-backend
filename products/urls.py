from rest_framework import routers

from products.views import ProductView

router = routers.SimpleRouter()
router.register('products', ProductView)
urlpatterns = router.urls
