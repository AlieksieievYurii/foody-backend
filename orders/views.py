from datetime import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotAcceptable
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from orders.models import Order, OrderExecution, History
from orders.serializers import OrderSerializer, OrderExecutionSerializer
from foody.permissions import IsAuthenticatedAndConfirmed, IsExecutor
from products.models import Product, Availability


@api_view(['GET'])
@permission_classes([IsAuthenticatedAndConfirmed, IsExecutor])
def get_current_order_execution(request):
    order_execution = OrderExecution.objects.filter(executor=request.user).first()
    if not order_execution:
        return Response('There is not current order', status=status.HTTP_404_NOT_FOUND)
    serializer = OrderExecutionSerializer(order_execution)
    return Response(serializer.data, status=status.HTTP_200_OK)


class OrderView(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                mixins.ListModelMixin,
                GenericViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticatedAndConfirmed]
    filter_backends = (OrderingFilter,)
    ordering_fields = ('timestamp',)

    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'product': openapi.Schema(type=openapi.TYPE_INTEGER),
        'count': openapi.Schema(type=openapi.TYPE_INTEGER)
    }))
    def create(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(pk=request.data.get('product'))
        except Product.DoesNotExist:
            return Response(f'Product with pk: {request.data.get("product")} not found',
                            status=status.HTTP_400_BAD_REQUEST)
        request.data['user'] = request.user.pk
        request.data['price'] = product.price
        request.data['cooking_time'] = product.cooking_time
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        availability = Availability.objects.get(product=serializer.validated_data['product'])
        if serializer.validated_data['count'] > availability.available:
            raise NotAcceptable(detail='You requested more than it exists')
        availability.available -= serializer.validated_data['count']
        availability.is_available = bool(availability.available)
        availability.save()
        super().perform_create(serializer)


class OrderExecutionView(viewsets.ModelViewSet):
    serializer_class = OrderExecutionSerializer
    queryset = OrderExecution.objects.all()
    permission_classes = [IsAuthenticatedAndConfirmed, IsExecutor]

    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'order': openapi.Schema(type=openapi.TYPE_INTEGER),
    }))
    def create(self, request, *args, **kwargs):
        try:
            Order.objects.get(pk=request.data.get('order'))
        except Order.DoesNotExist:
            return Response(f'Order with pk: {request.data.get("order")} not found', status=status.HTTP_400_BAD_REQUEST)
        request.data['executor'] = request.user.pk
        request.data['status'] = OrderExecution.Status.pending.name
        return super().create(request, *args, **kwargs)

    def perform_update(self, serializer):
        status = OrderExecution.Status(serializer.validated_data['status'])
        if status == OrderExecution.Status.delivered:
            self.create_history_item(order_execution_id=serializer.data['id'])
        else:
            super().perform_update(serializer)

    @staticmethod
    def create_history_item(order_execution_id: int):
        order_execution = OrderExecution.objects.get(pk=order_execution_id)
        History.objects.create(
            product=order_execution.order.product,
            user=order_execution.order.user,
            count=order_execution.order.count,
            price=order_execution.order.price,
            cooking_time=order_execution.order.cooking_time,
            timestamp=order_execution.order.timestamp,
            executor=order_execution.executor,
            finish_time=datetime.now(),
            delivery_address="Test"
        )
        order_execution.delete()
