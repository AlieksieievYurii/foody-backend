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


class OrderExecution(models.Model):
    class Status(models.TextChoices):
        PENDING = ('pending', 'pending')
        COOKING = ('cooking', 'cooking')
        FINISHED = ('finished', 'finished')
        DELIVERED = ('delivered', 'delivered')

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    executor = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField('role', choices=Status.choices, max_length=15, blank=False)

    class Meta:
        unique_together = ['order', 'executor']
