from rest_framework import viewsets

from permissions import IsAdministrator, IsAuthenticatedAndConfirmed
from products.models import Product
from products.serializers import ProductSerializer


class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]
