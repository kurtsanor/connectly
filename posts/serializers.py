from rest_framework import serializers
from .models import Post, Comment, Like
from users.models import User

class PostSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author']
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'author', 'post', 'created_at']
        read_only_fields = ['author', 'post']

        def validate_post(self, value):
            if not Post.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("Post not found.")
            return value


        def validate_author(self, value):
            if not User.objects.filter(id=value.id).exists():
                raise serializers.ValidationError("Author not found.")
            return value


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['post', 'author']