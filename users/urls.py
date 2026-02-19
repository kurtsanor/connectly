from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginView, GoogleAuthUrlView, GoogleCallbackView, GoogleLoginView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', LoginView.as_view()),
    path('auth/google/', GoogleAuthUrlView.as_view()),
    path('auth/google/callback/', GoogleCallbackView.as_view()),
    path('auth/google/login/', GoogleLoginView.as_view())
]