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
    CartSerializer
)
from .models import MenuItem, Category, Cart
from .permissions import IsManager, IsDeliveryCrew

# -------------- Cart  -----------------
# --------------------------------------
class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user.id)
        serialized_data = CartSerializer(cart_items, many=True).data
        return Response(serialized_data)
    
    def delete(self, request):
        cart_items = Cart.objects.filter(user=request.user.id)
        cart_items.delete()
        return Response({"details": "ok"})

    def post(self, request):
        data = request.data.copy()

        menuitem_id = data['menuitem']
        if not menuitem_id:
            return Response({"details": "Bad Request"}, status.HTTP_400_BAD_REQUEST)

        if not data.get("quantity"):
            data["quantity"] = 1
        try:
            quantity = int(data["quantity"])
        except Exception as e:
            return Response({"details": f"{type(e).__name__}:{e}"}, status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = Cart.objects.get(menuitem=menuitem_id, user=request.user.id)
        except ObjectDoesNotExist:
            menuitem = get_object_or_404(MenuItem, pk=menuitem_id)
            data['menuitem_id'] = menuitem_id
            data['unit_price'] = menuitem.price
            data['user'] = request.user.id
            data['price'] = menuitem.price * quantity
            cart_serializer = CartSerializer(data=data)
            if cart_serializer.is_valid():
                data = cart_serializer.validated_data
                cart_serializer.save()
        else:
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save()


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


class MenuItemsListCreateView(ManagerOnlyListCreateView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
class MenuItemsRUDView(ManagerOnlyRUDView):
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