from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User


class Product(models.Model):
    name = models.CharField('name', max_length=40, blank=False)
    description = models.CharField('description', max_length=300, blank=False)
    price = models.FloatField('price')
    cooking_time = models.IntegerField('cooking_time')


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_url = models.CharField('image_url', max_length=200, blank=False)
    is_default = models.BooleanField('is_default', default=True)
    is_external = models.BooleanField('is_external', default=False)


class FeedBack(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField('rating', validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ])


class Availability(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    available = models.IntegerField('available', validators=[MinValueValidator(0)])
    is_available = models.BooleanField('is_available', default=True)
    is_active = models.BooleanField('is_active', default=True)


class Category(models.Model):
    name = models.CharField('name', max_length=20, blank=False)
    icon_url = models.CharField('icon_url', max_length=200, blank=False)
    is_icon_external = models.BooleanField('is_icon_external', default=False)


class ProductCategory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    category = models.OneToOneField(Category, on_delete=models.CASCADE)