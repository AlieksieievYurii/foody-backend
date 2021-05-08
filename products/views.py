from cloudinary import uploader
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, views, status, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from permissions import IsAdministrator, IsAuthenticatedAndConfirmed
from products.models import Product, ProductImage, Availability
from products.serializers import ProductSerializer, ProductImageSerializer, AvailabilitySerializer


class ImageUploadView(views.APIView):
    @staticmethod
    def post(request):
        file_obj: InMemoryUploadedFile = request.data.get('file')
        if not file_obj:
            raise ValidationError('File must be specified', code=status.HTTP_400_BAD_REQUEST)

        response = uploader.upload(file_obj.read())

        return Response(data={'url': response['secure_url']}, status=204)


class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]


class ProductImageView(viewsets.ModelViewSet):
    serializer_class = ProductImageSerializer
    queryset = ProductImage.objects.all()
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]


class AvailabilityView(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    serializer_class = AvailabilitySerializer
    queryset = Availability.objects.all()
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']
    lookup_field = 'product'
