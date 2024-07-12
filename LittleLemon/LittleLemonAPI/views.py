import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.authentication import (
    TokenAuthentication,
    SessionAuthentication
)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .serializers import (
    MenuItemSerializer,
    CategorySerializer,
    UserSerializer,
    CartSerializer,
    OrderSerializer
)
from .models import MenuItem, Category, CartItem, Order, OrderItem
from .permissions import IsManager, IsDeliveryCrew

# -------------- Cart  -----------------
# --------------------------------------
class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user.id)
        serialized_data = CartSerializer(cart_items, many=True).data
        return Response(serialized_data)
    
    def delete(self, request):
        cart_items = CartItem.objects.filter(user=request.user.id)
        cart_items.delete()
        return Response({"details": "ok"})

    def post(self, request):
        data = request.data.copy()

        menuitem_id = data.get('menuitem')
        if not menuitem_id:
            return Response(
                {"details": "MenuItem ID field required (menuitem)"},
                status.HTTP_400_BAD_REQUEST
            )

        if not data.get("quantity"):
            data["quantity"] = 1
        try:
            quantity = int(data["quantity"])
        except Exception as e:
            return Response({"details": f"{type(e).__name__}:{e}"}, status.HTTP_400_BAD_REQUEST)
        if quantity < 1:
            return Response({"details": "Quantity must be at least 1"}, status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = CartItem.objects.get(menuitem=menuitem_id, user=request.user.id)
        except ObjectDoesNotExist:
            get_object_or_404(MenuItem, pk=menuitem_id)
            data['user_id'] = request.user.id
            data['menuitem_id'] = menuitem_id
            data['quantity'] = quantity
            cart_serializer = CartSerializer(data=data)
            if cart_serializer.is_valid():
                cart_serializer.save()
            else:
                return Response(cart_serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save()

        return Response({"details": "ok"})
            

# -------------- Orders  -----------------
# ----------------------------------------
class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if IsManager().has_permission(request):
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user.id)
        serialized_data = OrderSerializer(orders, many=True).data
        return Response(serialized_data)

    def post(self, request):
        cart_items = CartItem.objects.filter(user=request.user.id)
        if not cart_items:
            return Response({"details": "No items in cart!"}, status.HTTP_400_BAD_REQUEST)
        
        data = {'user_id': request.user.id, 'date': datetime.date.today()}
        context = {'cart_items': cart_items}
        order_serializer = OrderSerializer(data=data, context=context)
        if order_serializer.is_valid():
            new_order = order_serializer.save()
        else:
            return Response(order_serializer.errors, status.HTTP_400_BAD_REQUEST)
        
        for c_item in cart_items:
            OrderItem.objects.create(
                order=new_order,
                menuitem=MenuItem.objects.get(pk=c_item.menuitem.id), #type:ignore
                quantity=c_item.quantity,
                unit_price=c_item.unit_price,
                price=c_item.price
            )
            
        cart_items.delete()
        return Response({"details": "ok"})
    
    def delete(self, request, pk=None):
        if not IsManager().has_permission(request):
            return Response({'details': "Not Authorized"}, status.HTTP_403_FORBIDDEN)
        
        if pk is None:
            return Response(
                {'details': "Order ID must be specified in endpoint /orders/<int:orderid>"},
                status.HTTP_400_BAD_REQUEST
            )
        
        order = Order.objects.filter(id=pk)
        order.delete()
        return Response({"details": "ok"}) 



# ----- Categories and Menu Items  -------
# --------------------------------------
class ManagerOnlyListCreateView(ListCreateAPIView):
    ''' Abstract List/Create class for Manager Permissions '''
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != "GET":
            permission_classes += [IsManager]
        return [permission() for permission in permission_classes]

class ManagerOnlyRUDView(RetrieveUpdateDestroyAPIView):
    ''' Abstract Retrieve/Update/Destroy class for Manager Permissions '''        
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method != "GET":
            permission_classes += [IsManager]
        return [permission() for permission in permission_classes]


class CategoryListCreateView(ManagerOnlyListCreateView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryRUDView(ManagerOnlyRUDView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemListCreateView(ManagerOnlyListCreateView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
class MenuItemRUDView(ManagerOnlyRUDView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer





# ----- Group Management --------------
# -------------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsManager])
def list_create_managers(request):
    manager_group = Group.objects.get(name="Manager")

    if request.method == "GET":
        managers = manager_group.user_set.all()
        user_serializer = UserSerializer(managers, many=True)
        return Response(user_serializer.data)
    
    if request.method == "POST":
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            manager_group.user_set.add(user)
            return Response({"details": "ok"})
        else:
            return Response({"details": "Bad Request"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsManager])
def list_create_delivery_crew(request):
    manager_group = Group.objects.get(name="Delivery crew")

    if request.method == "GET":
        managers = manager_group.user_set.all()
        user_serializer = UserSerializer(managers, many=True)
        return Response(user_serializer.data)
    
    if request.method == "POST":
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            manager_group.user_set.add(user)
            return Response({"details": "ok"})
        else:
            return Response({"details": "Bad Request"}, status.HTTP_400_BAD_REQUEST)    

@api_view(['DELETE'])
@permission_classes([IsManager])
def remove_manager(request, pk):
    user = get_object_or_404(User, id=pk)    
    manager_group = Group.objects.get(name="Manager")
    manager_group.user_set.remove(user)
    return Response({"detail": "ok"})

@api_view(['DELETE'])
@permission_classes([IsManager])
def remove_delivery_crew(request, pk):
    user = get_object_or_404(User, id=pk)
    deliver_crew_group = Group.objects.get(name="Delivery crew")
    deliver_crew_group.user_set.remove(user)
    return Response({"detail": "ok"})