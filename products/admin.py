from django.contrib import admin

from products.forms import ProductImageForm
from products.models import *


class ProductImageAdmin(admin.ModelAdmin):
    form = ProductImageForm


admin.site.register(Product)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(FeedBack)
admin.site.register(Availability)
admin.site.register(Category)
admin.site.register(ProductCategory)
