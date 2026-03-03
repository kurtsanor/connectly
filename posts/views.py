from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
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
from .pagination import CommentPagination, PostPagination
from rest_framework import serializers

# Create your views here.
class PostListCreate(APIView):
    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]
    
    logger = LoggerSingleton().get_logger()
    
    def get(self, request):
        self.logger.info("Retrieving all posts...")
        # add comments and likes count
        posts = Post.objects.annotate(
            like_count=Count('post_likes', distinct=True),
            comment_count=Count('comments', distinct=True)
        )
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        self.logger.info("Creating new post...")
        self.logger.info(f"User is: {self.request.user}")
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        try:
            post = PostFactory.create_post(
                title=data.get('title'),
                content=data.get('content', ''),
                post_type=data.get('post_type'),
                metadata=data.get('metadata'),
                author=self.request.user,
            )
            response_serializer = PostSerializer(post)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            raise ValidationError(detail=str(e))
    
class CommentCreateView(APIView):
    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    logger = LoggerSingleton().get_logger()

    # comment on post endpoint
    def post(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        self.logger.info(f"Commenting on post id: {post.id}...")
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentListView(APIView):
    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination

    logger = LoggerSingleton().get_logger()
    # get comments of a post
    def get(self, request, post_id):
        post = Post.objects.get(pk=post_id)
        self.logger.info(f"Retrieving paginated comments of post id: {post.id}...")
        comments = post.comments.all()

        paginator = self.pagination_class()

        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            self.logger.info("Returning paginated data...")
            serializer = CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CommentSerializer(comments, many=True) # true = tell DRF that comments is a list
        return Response(serializer.data)
    

class PostLikeView(APIView):
    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    logger = LoggerSingleton().get_logger()

    # liking a post
    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            self.logger.info(f"Liking post id: {post.id}...")
            self.logger.info(f"user is: {request.user.id}")
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found")
        # check if already liked
        is_liked = Like.objects.all().filter(post=post, author=request.user).exists()
        
        if is_liked:
            return Response({'message': 'You already liked this post'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response({'message': 'Liked',
                             'data': serializer.data,
                             }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PostDetailView(APIView):
    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated, isAuthor]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            self.check_object_permissions(request, post)
            serializer = PostSerializer(post)
            data = serializer.data
            data['like_count'] = post.post_likes.count()
            data['comment_count'] = post.comments.count()
            return Response(data)
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_404_NOT_FOUND)

    
class FeedView(APIView):
    pagination_class = PostPagination
    authentication_classes = [JwtAuthentication]
    permission_classes=[IsAuthenticated]

    VALID_FILTERS = ['liked', 'followed']

    def get(self, request):
        posts = Post.objects.annotate(
            like_count=Count('post_likes', distinct=True),
            comment_count=Count('comments', distinct=True)).order_by('-created_at')

        filter = request.query_params.get('show', '').lower()
        
        if filter and filter not in self.VALID_FILTERS:
            return Response(
                {'error': f'Invalid filter. Valid options are: {self.VALID_FILTERS}'},
                status=status.HTTP_400_BAD_REQUEST)
        
        if filter == "liked":
            posts = posts.filter(post_likes__author=request.user)

        elif filter == "followed":
            posts = posts.filter(author__following__follower=request.user)
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request)

        if page is not None:
            serializer = PostSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

