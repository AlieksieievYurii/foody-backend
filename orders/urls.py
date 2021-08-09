from django.urls import path
from rest_framework import routers

from orders.views import OrderView, OrderExecutionView, get_current_order_execution, HistoryView

router = routers.SimpleRouter()
router.register('history', HistoryView)
router.register('execution', OrderExecutionView)
router.register('', OrderView)

urlpatterns = router.urls + [
    path('current_order_execution', get_current_order_execution),
]
