from django.urls import path

from . import views

urlpatterns = [
    path('categories', views.CategoryListCreateView.as_view()),
    path('menu-items', views.MenuItemsListCreateView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemsRUDView.as_view()),

    path('cart/menu-items', views.CartAPIView.as_view()),

    path('groups/manager/users', views.list_create_managers),
    path('groups/manager/users/<int:pk>', views.remove_manager),
    path('groups/delivery-crew/users', views.list_create_delivery_crew),
    path('groups/delivery-crew/users/<int:pk>', views.remove_delivery_crew),
]