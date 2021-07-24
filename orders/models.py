from django.core.validators import MinValueValidator
from django.db import models

from products.models import Product
from users.models import User


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField('count', validators=[MinValueValidator(0)])
    price = models.FloatField('price')
    cooking_time = models.IntegerField('cooking_time')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} for {self.user.first_name}'
