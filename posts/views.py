from django.shortcuts import render
from rest_framework import viewsets
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import isAuthor

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all() # tells DRF which objects/model to operate on.
    serializer_class = PostSerializer # tells DRF how to convert model instances to JSON and validate incoming data.
    permission_classes=[IsAuthenticated, isAuthor]
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes=[IsAuthenticated, isAuthor]

    def perform_create(self, serializer): 
        serializer.save(author=self.request.user)
