from django.contrib import admin

from users.models import User, UserRole

admin.site.register(User)
admin.site.register(UserRole)