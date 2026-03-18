from rest_framework import serializers
from .models import Post, Comment, Like
from users.models import User

class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post objects.
    Includes computed fields for like and comment counts.
    """
    like_count = serializers.IntegerField(read_only=True)   # Annotated in views
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author']  # Author is always set from request.user, not client input


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment objects.
    Ensures author and post are read-only (set by the system).
    """
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']
        read_only_fields = ['author', 'post']

        # Validation methods ensure referenced objects exist.
        def validate_post(self, value):
            if not Post.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("Post not found.")
            return value

        def validate_author(self, value):
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("Author not found.")
            return value


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Like objects.
    Ensures post and author are read-only (set by the system).
    """
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['post', 'author']
