from rest_framework import routers

from products.views import ProductView

router = routers.SimpleRouter()
router.register('', ProductView)
urlpatterns = router.urls
