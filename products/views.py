from rest_framework import viewsets

from permissions import IsAdministrator, IsAuthenticatedAndConfirmed
from products.models import Product, ProductImage
from products.serializers import ProductSerializer, ProductImageSerializer


class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]


class ProductImageView(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    queryset = ProductImage.objects.all()
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]