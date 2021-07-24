from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from orders.models import Order
from orders.serializers import OrderSerializer
from permissions import IsAuthenticatedAndConfirmed
from products.models import Product


class OrderView(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                mixins.ListModelMixin,
                GenericViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticatedAndConfirmed]

    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'product': openapi.Schema(type=openapi.TYPE_INTEGER),
        'count': openapi.Schema(type=openapi.TYPE_INTEGER)
    }))
    def create(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(pk=request.data['product'])
        except Product.DoesNotExist:
            return Response(f'Product with pk: {request.data["product"]} not found', status=status.HTTP_400_BAD_REQUEST)
        request.data['user'] = request.user.pk
        request.data['price'] = product.price
        request.data['cooking_time'] = product.cooking_time
        return super().create(request, *args, **kwargs)
