from rest_framework import serializers
from .models import User, Follow

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User objects.
    Handles user creation and ensures sensitive fields are properly managed.
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password',
            'first_name', 'last_name', 'google_id',
            'avatar', 'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True},   # Dont expose passwords in responses
            'first_name': {'required': True},   # Enforce required fields
            'last_name': {'required': True},
            'role': {'required': True}
        }
        read_only_fields = ['google_id']  # Google ID is system-managed, not client-supplied


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for Follow relationships.
    Represents a user following another user.
    """
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower']  # Follower is always set from request.user


class GoogleCallbackSerializer(serializers.Serializer):
    """
    Serializer for handling Google OAuth callback.
    Expects an authorization code from the client.
    """
    code = serializers.CharField()  # Authorization code returned by Google
