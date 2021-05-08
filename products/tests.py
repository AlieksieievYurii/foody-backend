from rest_framework import status

from products.models import Product, ProductImage, Availability
from users.models import UserRole
from utils.tests import ApiTestCase


class ProductsTestCase(ApiTestCase):
    @ApiTestCase.Decorators.create_default_user_and_log_in()
    def test_get_products(self):
        Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        Product.objects.create(name='Product Two', description='Product Description', price=2.25, cooking_time=1600)

        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Product.objects.all().count())

    @ApiTestCase.Decorators.create_default_user_and_log_in()
    def test_get_product(self):
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        Product.objects.create(name='Product Two', description='Product Description', price=2.25, cooking_time=1600)

        response = self.client.get(f'/products/{p.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], p.pk)
        self.assertEqual(response.data['name'], p.name)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.client)
    def test_create_product_client(self):
        response = self._create_product()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.executor)
    def test_create_product_executor(self):
        response = self._create_product()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.administrator)
    def test_create_product_administrator(self):
        response = self._create_product()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.administrator)
    def test_delete_product_administrator(self):
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        response = self.client.delete(f'/products/{p.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.all().count(), 0)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.executor)
    def test_delete_product_executor(self):
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        response = self.client.delete(f'/products/{p.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.all().count(), 1)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.administrator)
    def test_update_product_administrator(self):
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        response = self.client.patch(f'/products/{p.pk}/',
                                     {
                                         'name': 'Product Name Two'
                                     })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.all().count(), 1)
        self.assertEqual(Product.objects.get(pk=p.pk).name, 'Product Name Two')

    def _create_product(self):
        return self.client.post('/products/', {
            'name': 'Product One',
            'description': 'Description',
            'price': 1.50,
            'cooking_time': 3600
        })


class ProductImageTestCase(ApiTestCase):
    @ApiTestCase.Decorators.create_default_user_and_log_in()
    def test_get_product_images(self):
        p1 = Product.objects.create(name='Product One', description='Product Description', price=1.25,
                                    cooking_time=3600)
        p2 = Product.objects.create(name='Product Two', description='Product Description', price=2.25,
                                    cooking_time=1600)
        ProductImage.objects.create(product=p1, image_url="http://image")
        ProductImage.objects.create(product=p2, image_url="http://image", is_default=False)

        response = self.client.get('/products/images/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], ProductImage.objects.all().count())

    @ApiTestCase.Decorators.create_default_user_and_log_in()
    def test_get_product_image(self):
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25,
                                   cooking_time=3600)
        pi_1 = ProductImage.objects.create(product=p, image_url="http://image", is_default=False)

        response = self.client.get(f'/products/images/{pi_1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], pi_1.pk)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.administrator)
    def test_create_product_image_administrator(self):
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25,
                                   cooking_time=3600)

        response = self.client.post(f'/products/images/', {
            'image_url': 'https://image',
            'is_default': True,
            'is_external': False,
            'product': p.pk
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], p.pk)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.client)
    def test_create_product_image_client(self):
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25,
                                   cooking_time=3600)

        response = self.client.post(f'/products/images/', {
            'image_url': 'https://image',
            'is_default': True,
            'is_external': False,
            'product': p.pk
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ProductImage.objects.all().count(), 0)


class AvailabilityTestCase(ApiTestCase):
    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.client)
    def test_get_availability(self):
        p1 = Product.objects.create(name='Product One', description='Description', price=1.25, cooking_time=3600)
        p2 = Product.objects.create(name='Product Two', description='Description', price=2.25, cooking_time=1600)
        a1 = Availability.objects.create(product=p1, available=10)
        Availability.objects.create(product=p2, available=20)

        response = self.client.get(f'/products/availabilities/?product={p1.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], a1.pk)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.administrator)
    def test_update_availability(self):
        p1 = Product.objects.create(name='Product One', description='Description', price=1.25, cooking_time=3600)
        p2 = Product.objects.create(name='Product Two', description='Description', price=2.25, cooking_time=1600)
        a1 = Availability.objects.create(product=p1, available=10)
        a2 = Availability.objects.create(product=p2, available=20)

        response = self.client.patch(f'/products/availabilities/{a1.pk}/', {
            'available': 5
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertEqual(a1.available, 5)
        self.assertEqual(a2.available, 20)

    @ApiTestCase.Decorators.create_default_user_and_log_in(role=UserRole.UserRoleChoice.executor)
    def test_update_availability_executor(self):
        p1 = Product.objects.create(name='Product One', description='Description', price=1.25, cooking_time=3600)
        a1 = Availability.objects.create(product=p1, available=10)

        response = self.client.patch(f'/products/availabilities/{a1.pk}/', {
            'available': 5
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        a1.refresh_from_db()
        self.assertEqual(a1.available, 10)
