from django.db import models
# from users.models import User
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    POST_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
    metadata = models.JSONField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]
    
class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    
    class Meta:
        unique_together = ('post', 'author')

    def __str__(self):
        return f"Post {self.post.id} liked by {self.author.username}"