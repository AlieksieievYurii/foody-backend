from cloudinary import uploader
from django.core.files.uploadedfile import InMemoryUploadedFile
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, views, status, mixins, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from permissions import IsAdministrator, IsAuthenticatedAndConfirmed
from products.models import Product, ProductImage, Availability, Category, ProductCategory, Feedback
from products.serializers import ProductSerializer, ProductImageSerializer, AvailabilitySerializer, CategorySerializer, \
    ProductCategorySerializer, FeedbackSerializer


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
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['availability__is_available', 'availability__is_active']


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

    def get_queryset(self):
        product_query = self.request.query_params.get('product_ids', None)
        if product_query:
            products = product_query.split(',')
            return super().get_queryset().filter(product_id__in=products)
        else:
            return super().get_queryset()

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(name='product_ids', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]


class ProductCategoryView(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer
    queryset = ProductCategory.objects.all()
    permission_classes = [IsAdministrator, IsAuthenticatedAndConfirmed]


class FeedbackView(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    permission_classes = [IsAuthenticatedAndConfirmed]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']
    lookup_field = 'product'

    @swagger_auto_schema(request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'product': openapi.Schema(type=openapi.TYPE_INTEGER),
        'rating': openapi.Schema(type=openapi.TYPE_INTEGER)
    }))
    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        return super().create(request, *args, **kwargs)
