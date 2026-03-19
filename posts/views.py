from rest_framework import viewsets, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Count

from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from .permissions import isAuthor
from .factories.post_factory import PostFactory
from .pagination import CommentPagination, PostPagination
from users.permissions import IsAuthenticated, IsAdmin
from users.authentication import JwtAuthentication
from connectly.singletons.logger_singleton import LoggerSingleton
from connectly.singletons.paginator_singleton import PostPaginatorSingleton, CommentPaginatorSingleton
from django.db.models import Q
from django.core.cache import cache

# Instantiate the global singletons once for shared use across all views.
logger = LoggerSingleton().get_logger()
comment_paginator = CommentPaginatorSingleton.get_instance()
post_paginator = PostPaginatorSingleton.get_instance()


class PostListCreate(APIView):
    """
    Handles listing all posts and creating new ones.

    GET  /posts/      — Returns all posts with like and comment counts.
    POST /posts/      — Creates a new post using the PostFactory.
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves all posts annotated with their like and comment counts.
        """

        logger.info("Retrieving all posts...")

        # Annotate each post with aggregated like and comment counts in a single query.
        all_posts = Post.objects.annotate(
            like_count=Count('post_likes', distinct=True),
            comment_count=Count('comments', distinct=True)
        )

        post_serializer = PostSerializer(all_posts, many=True)  # many=True tells DRF to serialize a list.
        return Response(post_serializer.data)

    def post(self, request):
        """
        Creates a new post for the authenticated user using the PostFactory.

        Validates the incoming data, then delegates post creation to the
        PostFactory to handle type-specific construction logic.
        """

        logger.info("Creating new post...")
        logger.info(f"Requested by user: {request.user}")

        post_serializer = PostSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)
        validated_post_data = post_serializer.validated_data

        try:
            # Delegate post creation to the factory to handle type-specific logic.
            new_post = PostFactory.create_post(
                title=validated_post_data.get('title'),
                content=validated_post_data.get('content', ''),
                post_type=validated_post_data.get('post_type'),
                metadata=validated_post_data.get('metadata'),
                privacy=validated_post_data.get('privacy'),
                author=request.user,
            )
            response_serializer = PostSerializer(new_post)

            feed_current_version = cache.get('feed_version', 0)
            cache.set('feed_version', feed_current_version + 1)

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as post_creation_error:
            raise ValidationError(detail=str(post_creation_error))


class CommentCreateView(APIView):
    """
    Handles creating a new comment on a specific post.

    POST /posts/<post_id>/comments/ — Adds a comment to the specified post.
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        """
        Creates a new comment on the specified post authored by the authenticated user.
        """

        target_post = Post.objects.get(pk=post_id)
        logger.info(f"Adding comment to post id: {target_post.id}...")

        comment_serializer = CommentSerializer(data=request.data)

        if comment_serializer.is_valid():
            comment_serializer.save(post=target_post, author=request.user)
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)

        return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListView(APIView):
    """
    Handles paginated retrieval of comments for a specific post.

    GET /posts/<post_id>/comments/ — Returns a paginated list of comments on the post.
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        """
        Retrieves a paginated list of comments for the specified post.

        Uses the CommentPagination class to split results into pages.
        Returns all comments unpaginated if pagination is not applicable.
        """

        target_post = Post.objects.get(pk=post_id)
        logger.info(f"Retrieving paginated comments for post id: {target_post.id}...")

        post_comments = target_post.comments.all()

        # Instantiate the paginator and attempt to paginate the comment queryset.
        paginated_comments = comment_paginator.paginate_queryset(post_comments, request)

        if paginated_comments is not None:
            logger.info("Returning paginated comment data...")
            comment_serializer = CommentSerializer(paginated_comments, many=True)
            return comment_paginator.get_paginated_response(comment_serializer.data)

        # Fall back to returning all comments if pagination is not triggered.
        comment_serializer = CommentSerializer(post_comments, many=True)    # many=True tells DRF to serialize a list.
        return Response(comment_serializer.data)
    
class CommentDetailView(APIView):
    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]

    # deletion of comment
    def delete(self, request, post_id, comment_id):
        # check if post exists first
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"Message": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Get the specific for the post
            comment = post.comments.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"Message": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        # delete the comment
        comment.delete()
        return Response({"Message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class PostLikeView(APIView):
    """
    Handles liking a specific post.

    POST /posts/<post_id>/like/ — Adds a like to the specified post for the authenticated user.
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        """
        Creates a like on the specified post for the authenticated user.

        Prevents duplicate likes by checking if the user has already liked the post.
        """
        try:
            target_post = Post.objects.get(pk=post_id)
            logger.info(f"User {request.user.id} is liking post id: {target_post.id}...")
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found.")

        # Check if the user has already liked this post to prevent duplicate likes.
        already_liked = Like.objects.filter(post=target_post, author=request.user).exists()

        if already_liked:
            return Response({'message': 'You have already liked this post.'}, status=status.HTTP_400_BAD_REQUEST)

        like_serializer = LikeSerializer(data=request.data)

        if like_serializer.is_valid():
            like_serializer.save(post=target_post, author=request.user)
            return Response({
                'message': 'Post liked successfully.',
                'data':    like_serializer.data,
            }, status=status.HTTP_201_CREATED)

        return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """
    Handles retrieval of a single post by its ID.
    
    GET /posts/<post_id>/ — Returns the post details including like and comment counts.
                            Only accessible by the post's author.
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), isAuthor()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    def get(self, request, post_id):
        """
        Retrieves a single post by ID, including its like and comment counts.

        Enforces object-level permissions to ensure only the post's author
        can access this endpoint.
        """
        try:
            target_post = Post.objects.get(pk=post_id)

            if target_post.privacy == 'public':
                pass
            elif target_post.privacy == 'private':
                self.check_object_permissions(request, target_post)     # Enforce author-only access.

            post_serializer = PostSerializer(target_post)
            post_data = post_serializer.data

            # Append live counts directly to the response payload.
            post_data['like_count'] = target_post.post_likes.count()
            post_data['comment_count'] = target_post.comments.count()
        
            return Response(post_data)

        except Post.DoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_404_NOT_FOUND)
       
    def delete(self, request, post_id):
        """
        Handles deletion of post by ID.
        """

        try:
            target_post = Post.objects.get(pk=post_id)
            target_post.delete()
            return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({"error": "Post does not exist."}, status=status.HTTP_404_NOT_FOUND)

class FeedView(APIView):
    """
    Handles retrieving a paginated feed of posts with optional filtering.

    GET /feed/               — Returns all posts ordered by most recent.
    GET /feed/?show=liked    — Returns only posts liked by the authenticated user.
    GET /feed/?show=followed — Returns only posts by users the authenticated user follows.
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    VALID_FILTERS = ['liked', 'followed']   # Accepted values for the 'show' query parameter.

    def get(self, request):
        """
        Retrieves a paginated feed of posts, optionally filtered by liked or followed.

        Applies the 'show' query parameter to filter the feed, then paginates
        the results using PostPagination.
        """

        active_filter = request.query_params.get('show', '').lower()
        active_page = request.query_params.get('page', '')
        page_size = request.query_params.get('page_size', '')

        # Reject requests with unrecognized filter values.
        if active_filter and active_filter not in self.VALID_FILTERS:
            return Response(
                {'error': f'Invalid filter. Valid options are: {self.VALID_FILTERS}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        feed_current_version = cache.get('feed_version', 0)

        cache_key = f"feed_user_{request.user.id}_page_{active_page}_size_{page_size}_filter_{active_filter}_version_{feed_current_version}"

        cached_feed = cache.get(cache_key)
        if cached_feed:
            logger.info(f"Feed cache hit for {request.user.email} (show={active_filter}, page={active_page}, page_size={page_size})")
            # Return cached result immediately without hitting the database.
            return Response(cached_feed)

        # Annotate all posts with counts and sort by newest first.
        feed_posts = Post.objects.annotate(
            like_count=Count('post_likes', distinct=True),
            comment_count=Count('comments', distinct=True)
        ).filter(
            Q(privacy='public') | Q(author=request.user, privacy='private') # Filter to show all public posts, as well as the private posts of authenticated user.
            ).order_by('-created_at')

        if active_filter == "liked":
            # Narrow the feed to posts the authenticated user has liked.
            feed_posts = feed_posts.filter(post_likes__author=request.user)

        elif active_filter == "followed":
            # Narrow the feed to posts authored by users the authenticated user follows.
            feed_posts = feed_posts.filter(author__following__follower=request.user)

        # Paginate the filtered post queryset.
        paginated_feed = post_paginator.paginate_queryset(feed_posts, request)

        if paginated_feed is not None:
            feed_serializer = PostSerializer(paginated_feed, many=True, context={'request': request})
            response_data = post_paginator.get_paginated_response(feed_serializer.data).data
            cache.set(cache_key, response_data, timeout=60*5) # Cache for 5 minutes.
            logger.info(f"Feed cache miss for {request.user.email} (show={active_filter}, page={active_page}, page_size={page_size})")
            return Response(response_data)

        feed_serializer = PostSerializer(feed_posts, many=True, context={'request': request})
        cache.set(cache_key, feed_serializer.data, timeout=60*5) # Cache for 5 minutes.
        return Response(feed_serializer.data)