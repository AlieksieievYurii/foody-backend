from django.contrib import admin

from products.models import *

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(FeedBack)
admin.site.register(Availability)
admin.site.register(Category)
admin.site.register(ProductCategory)