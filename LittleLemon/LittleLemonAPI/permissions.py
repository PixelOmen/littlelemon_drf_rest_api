from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        # Automatically returns true if SuperUser
        if request.user.is_staff:
            return True
        return request.user.groups.filter(name="Manager").exists()
    

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        # Automatically returns true if SuperUser
        if request.user.is_staff:
            return True
        return request.user.groups.filter(name="Delivery crew").exists()    