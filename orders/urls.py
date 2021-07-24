from rest_framework import routers

from orders.views import OrderView

router = routers.SimpleRouter()
router.register('', OrderView)

urlpatterns = router.urls
