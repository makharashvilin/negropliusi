from django.contrib import admin
from .models import Product, Category, CartItem, Cart

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
