from rest_framework import serializers

from orders.models import Order, OrderExecution, History


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderExecution
        fields = '__all__'


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'
