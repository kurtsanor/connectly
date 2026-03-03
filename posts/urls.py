from django.urls import path, include
from .views import PostListCreate, FeedView, PostDetailView, CommentCreateView, PostLikeView, CommentListView

urlpatterns = [
    path('posts/', PostListCreate.as_view()),
    path('posts/<int:post_id>/', PostDetailView.as_view()),
    path('posts/<int:post_id>/comments/', CommentListView.as_view()),
    path('posts/<int:post_id>/comment/', CommentCreateView.as_view()),
    path('posts/<int:post_id>/like/', PostLikeView.as_view()),
    path('feed/', FeedView.as_view())
]