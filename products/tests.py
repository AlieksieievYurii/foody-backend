from rest_framework import status

from products.models import Product
from users.models import UserRole
from utils.tests import ApiTestCase


class ProductsTestCase(ApiTestCase):
    def test_get_products(self):
        Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        Product.objects.create(name='Product Two', description='Product Description', price=2.25, cooking_time=1600)

        user = self._create_default_user_and_log_in()
        self._login(user)

        response = self.client.get('/products/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Product.objects.all().count())

    def test_get_product(self):
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        Product.objects.create(name='Product Two', description='Product Description', price=2.25, cooking_time=1600)

        user = self._create_default_user_and_log_in()
        self._login(user)

        response = self.client.get(f'/products/products/{p.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], p.pk)
        self.assertEqual(response.data['name'], p.name)

    def test_create_product_client(self):
        user = self._create_default_user_and_log_in(role=UserRole.UserRoleChoice.client)
        self._login(user)

        response = self._create_product()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_executor(self):
        user = self._create_default_user_and_log_in(role=UserRole.UserRoleChoice.executor)
        self._login(user)

        response = self._create_product()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_administrator(self):
        user = self._create_default_user_and_log_in(role=UserRole.UserRoleChoice.administrator)
        self._login(user)

        response = self._create_product()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_product_administrator(self):
        user = self._create_default_user_and_log_in(role=UserRole.UserRoleChoice.administrator)
        self._login(user)
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        response = self.client.delete(f'/products/products/{p.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.all().count(), 0)

    def test_delete_product_executor(self):
        user = self._create_default_user_and_log_in(role=UserRole.UserRoleChoice.executor)
        self._login(user)
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        response = self.client.delete(f'/products/products/{p.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.all().count(), 1)

    def test_update_product_administrator(self):
        user = self._create_default_user_and_log_in(role=UserRole.UserRoleChoice.administrator)
        self._login(user)
        p = Product.objects.create(name='Product One', description='Product Description', price=1.25, cooking_time=3600)
        response = self.client.patch(f'/products/products/{p.pk}/',
                                     {
                                         'name': 'Product Name Two'
                                     })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Product.objects.all().count(), 1)
        self.assertEqual(Product.objects.get(pk=p.pk).name, 'Product Name Two')

    def _create_product(self):
        return self.client.post('/products/products/', {
            'name': 'Product One',
            'description': 'Description',
            'price': 1.50,
            'cooking_time': 3600
        })
