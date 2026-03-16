from django.db import models

class User(models.Model):
    # Choices for the role field: stored value (e.g. "admin") and human-readable label (e.g. "Admin")
    ROLES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('guest', 'Guest')
    ]

    # Basic user information
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    password = models.TextField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    avatar = models.URLField(blank=True, null=True)

    # Role field: stored as a string, constrained by ROLES choices
    role = models.CharField(max_length=10, choices=ROLES, default='guest')

    # Timestamp automatically set when the user is created
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # Display username if available, otherwise fallback to email
        return self.username or self.email
    

class Follow(models.Model):
    # Self-referential relationship: both follower and following are Users
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    # Timestamp automatically set when the follow relationship is created
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Prevent duplicate follow relationships (same follower/following pair)
        unique_together = ('follower', 'following')

    def __str__(self):
        # Human-readable representation of the relationship
        return f"{self.follower} follows {self.following}"
