from django.contrib import admin

from orders.models import Order, OrderExecution

admin.site.register(Order)
admin.site.register(OrderExecution)
