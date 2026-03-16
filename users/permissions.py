from rest_framework.permissions import BasePermission
from .models import User

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "admin"
