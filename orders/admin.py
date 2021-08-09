from django.contrib import admin

from orders.models import Order, OrderExecution, History

admin.site.register(Order)
admin.site.register(OrderExecution)
admin.site.register(History)
