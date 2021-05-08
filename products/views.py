from cloudinary import uploader
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import viewsets, views, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from permissions import IsAdministrator, IsAuthenticatedAndConfirmed
from products.models import Product, ProductImage
from products.serializers import ProductSerializer, ProductImageSerializer


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
