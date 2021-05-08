from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User


class Product(models.Model):
    name = models.CharField('name', max_length=40, blank=False)
    description = models.CharField('description', max_length=300, blank=False)
    price = models.FloatField('price')
    cooking_time = models.IntegerField('cooking_time')

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_url = models.CharField('image_url', max_length=200, blank=False)
    is_default = models.BooleanField('is_default', default=True)
    is_external = models.BooleanField('is_external', default=False)

    def __str__(self):
        return f'{"Default " if self.is_default else ""}Image for [{self.product.name}]'


class FeedBack(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField('rating', validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ])

    class Meta:
        unique_together = ('product', 'user',)

    def __str__(self):
        return f'{self.user.email} -> [{self.rating}] for {self.product.name}'


class Availability(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    available = models.IntegerField('available', validators=[MinValueValidator(0)])
    is_available = models.BooleanField('is_available', default=True)
    is_active = models.BooleanField('is_active', default=True)

    def __str__(self):
        return f'[{self.product.name}] -> available: {self.available}'


class Category(models.Model):
    name = models.CharField('name', max_length=20, blank=False)
    icon_url = models.CharField('icon_url', max_length=200, blank=False)
    is_icon_external = models.BooleanField('is_icon_external', default=False)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.name} -> {self.category.name}'
