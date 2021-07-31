from rest_framework import serializers

from orders.models import Order, OrderExecution


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderExecution
        fields = '__all__'
