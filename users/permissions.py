from rest_framework.permissions import BasePermission
from .models import User

class IsAuthenticated(BasePermission):
    """
    Custom permission class to check if the request
    is made by a valid authenticated User instance.
    """

    def has_permission(self, request, view):
        """
        Grant permission if the request.user is a User object.
        """
        return isinstance(request.user, User)


class IsAdmin(BasePermission):
    """
    Custom permission class to restrict access
    so that only users with the 'admin' role can proceed.
    """

    def has_permission(self, request, view):
        """
        Grant permission if the requesting user has an admin role.
        """
        return request.user.role == "admin"
