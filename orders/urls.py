from rest_framework import routers

from orders.views import OrderView, OrderExecutionView

router = routers.SimpleRouter()
router.register('execution', OrderExecutionView)
router.register('', OrderView)

urlpatterns = router.urls
