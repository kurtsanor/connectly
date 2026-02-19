from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    password = models.TextField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username