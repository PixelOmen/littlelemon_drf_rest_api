from decimal import Decimal

from django.contrib.auth.models import User

from rest_framework import serializers

from .models import MenuItem, Category, Cart

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        
class CartSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    quantity = serializers.IntegerField()

    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price',
                  'price', 'menuitem_id']
    
