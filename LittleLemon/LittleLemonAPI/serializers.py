from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    MenuItem,
    Category,
    CartItem,
    Order,
    OrderItem
)

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
    '''
    Only needs `quantity` and `menuitem_id` for deserialization,
    the rest is calculated/retrieved in `create`.
    '''
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user'
    )
    menuitem_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(), write_only=True, source='menuitem'
    )
    menuitem = MenuItemSerializer(read_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'menuitem', 'quantity',
                  'unit_price', 'price', 'user_id', 'menuitem_id']
        read_only_fields = ['user']
        
    def create(self, validated_data):
        user = validated_data['user']
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']
        unit_price = menuitem.price
        price = menuitem.price * quantity

        return CartItem.objects.create(
            user=user,
            menuitem=menuitem,
            quantity=quantity,
            unit_price=unit_price,
            price=price
        )


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='user'
    )
    delivery_crew = UserSerializer(read_only=True)
    delivery_crew_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True,
        source='delivery_crew', required=False
    )
    orderitems = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status',
                  'total', 'date', 'user_id', 'delivery_crew_id', 'orderitems']
        read_only_fields = ['total']

    def get_orderitems(self, obj):
        orderitems = obj.orderitem_set.all()
        return OrderItemSerializer(orderitems, many=True).data
        
    def create(self, validated_data):
        user = validated_data['user']
        date = validated_data['date']
        total = sum([cartitem.price for cartitem in self.context['cart_items']])
        return Order.objects.create(
            user=user,
            total=total,
            date=date
        )
        

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['menuitem', 'quantity', 'unit_price', 'price']