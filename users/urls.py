from django.urls import path, include
from .views import UserListCreate, LoginView, GoogleAuthUrlView, GoogleCallbackView, GoogleLoginView, AvatarUploadView, FollowView

urlpatterns = [
    path('users/', UserListCreate.as_view()),
    path('users/avatar/', AvatarUploadView.as_view()),
    path('users/<int:user_id>/follow/', FollowView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/google/', GoogleAuthUrlView.as_view()),
    path('auth/google/callback/', GoogleCallbackView.as_view()),
    path('auth/google/login/', GoogleLoginView.as_view()),
]