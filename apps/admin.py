from django.contrib import admin

# Register your models here.

from .models import Product, Profile, Inventory

admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(Inventory)