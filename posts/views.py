from django.shortcuts import render
from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all() # tells DRF which objects/model to operate on.
    serializer_class = PostSerializer # tells DRF how to convert model instances to JSON and validate incoming data.