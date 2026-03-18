from django.db import models
from users.models import User

class Post(models.Model):
    """
    Represents a user-created post in the system.
    Supports multiple types (text, image, video) and privacy settings.
    """

    POST_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    PRIVACY_TYPES = [
        ('public', 'Public'),
        ('private', 'Private')
    ]

    # Core post fields
    title = models.CharField(max_length=255)  # Short title for the post
    content = models.TextField(blank=True)    # Main body content, optional for non-text posts
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')  # Type of post
    metadata = models.JSONField(null=True, blank=True)  # Extra data (e.g., file size, duration)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')  # Creator of the post
    privacy = models.CharField(max_length=10, choices=PRIVACY_TYPES, default='public')  # Visibility setting
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when post was created

    def __str__(self):
        # Return a preview of the post content for admin/debug readability
        return self.content[:50]
    

class Comment(models.Model):
    """
    Represents a comment made by a user on a specific post.
    """

    text = models.TextField()  # Content of the comment
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')  # Comment creator
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')    # Associated post
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when comment was created
    
    def __str__(self):
        # Show author and post ID for quick identification
        return f"Comment by {self.author.username} on Post {self.post.id}"


class Like(models.Model):
    """
    Represents a 'like' reaction by a user on a post.
    Each user can only like a post once.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')  # Liked post
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')  # User who liked

    class Meta:
        # Prevent duplicate likes by the same user on the same post
        unique_together = ('post', 'author')

    def __str__(self):
        # Show post ID and author for quick identification
        return f"Post {self.post.id} liked by {self.author.username}"
