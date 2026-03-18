from rest_framework.permissions import BasePermission

class isAuthor(BasePermission):
    """
    Custom permission class to restrict access
    so that only the author of an object can perform certain actions.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the requesting user is the author of the object.
        """
        # Allow access only if the object's author matches the authenticated user.
        return obj.author == request.user
