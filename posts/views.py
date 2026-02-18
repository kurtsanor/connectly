from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from users.permissions import IsAuthenticated
from .permissions import isAuthor
from .factories.post_factory import PostFactory
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from users.authentication import JwtAuthentication
from connectly.singletons.logger_singleton import LoggerSingleton
from .pagination import CommentPagination

# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all() # tells DRF which objects/model to operate on.
    serializer_class = PostSerializer # tells DRF how to convert model instances to JSON and validate incoming data.
    authentication_classes = [JwtAuthentication]
    permission_classes=[IsAuthenticated, isAuthor]
    
    logger = LoggerSingleton().get_logger()
    
    def get_queryset(self):
        self.logger.info("Retrieving all posts...")
        # add comments and likes count
        return self.queryset.annotate(
            like_count=Count('post_likes', distinct=True),
            comment_count=Count('comments')
        )
    
    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()

        serializer = self.get_serializer(post)

        self.logger.info(f"Retrieving post id: {post.id}...")

        data = serializer.data
        # add comment and like count
        data['like_count'] = post.post_likes.count()
        data['comment_count'] = post.comments.count()
        return Response(data)

    def perform_create(self, serializer):
        self.logger.info("Creating new post...")
        self.logger.info(f"User is: {self.request.user}")
        data = serializer.validated_data
        
        try:
            instance = PostFactory.create_post(
                title=data.get('title'),
                content=data.get('content'),
                post_type=data.get('post_type'),
                metadata=data.get('metadata'),
                author=self.request.user,
            )

            serializer.instance = instance
        except ValueError as e:
            raise ValidationError(detail=str(e))
        
    # comment on post endpoint
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        self.logger.info(f"Commenting on post id: {post.id}...")
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # get comments of a post
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        post = self.get_object()
        self.logger.info(f"Retrieving paginated comments of post id: {post.id}...")
        comments = post.comments.all()

        self.pagination_class = CommentPagination

        page = self.paginate_queryset(comments)
        if page is not None:
            self.logger.info("Returning paginated data...")
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CommentSerializer(comments, many=True) # true = tell DRF that comments is a list
        return Response(serializer.data)
    
    # liking a post
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        self.logger.info(f"Liking post id: {post.id}...")
        self.logger.info(f"user is: {request.user.id}")
        # check if already liked
        is_liked = Like.objects.all().filter(post=post, author=request.user.id).exists()
        
        if is_liked:
            return Response({'message': 'You already liked this post'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response({'message': 'Liked',
                             'data': serializer.data,
                             }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)