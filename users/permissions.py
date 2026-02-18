from rest_framework.permissions import BasePermission
from .models import User

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, User)
