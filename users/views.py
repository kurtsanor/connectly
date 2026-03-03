from django.shortcuts import render
from rest_framework import viewsets, status
from .models import User, Follow
from .serializers import GoogleCallbackSerializer, UserSerializer, FollowSerializer
from .permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
from .authentication import JwtAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .services.google_oauth import exchange_code, get_google_auth_url, get_user_info
from connectly.singletons.logger_singleton import LoggerSingleton
from .services.jwt import generate_token
from rest_framework import serializers
from .services.cloudinary import upload_avatar

logger = LoggerSingleton().get_logger()

# Create your views here.
class UserListCreate(APIView):
    authentication_classes=[JwtAuthentication]

    def get_permissions(self):
        if self.request.method == 'create':  # register is public
            return []
        return [IsAuthenticated()]
    
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # registering a user
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise serializers.ValidationError(
                {"username": "This field is required", 
                 "password": "This field is required"}
                )
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            hashed_password = make_password(password)
            serializer.save(password=hashed_password)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            raise serializers.ValidationError(
                {"username": "This field is required", 
                 "password": "This field is required"}
                )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({'error': "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = generate_token(user)

        return Response({"message": "Login successful", 'token': token}, status=status.HTTP_200_OK)
    
class GoogleAuthUrlView(APIView):
    def get(self, request):
        return Response({"auth_url": get_google_auth_url()})
    
    
class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.query_params.get('code')
        if not code:
            return Response({"error": "code not found"}, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"code is: {code}")
        return Response({"code": code})
    

class GoogleLoginView(APIView): 
    def post(self, request):
        serializer = GoogleCallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tokens = exchange_code(serializer.validated_data["code"])
            user_info = get_user_info(tokens["access_token"])

            user_email = user_info.get('email')

            # check if email exists. if yes, link the google id to the user's existing account
            existing_user = User.objects.filter(email=user_email).first()

            if existing_user and not existing_user.google_id:
                existing_user.google_id = user_info.get('sub')
                existing_user.save()
                return Response({"user": UserSerializer(existing_user).data, 
                             "message": "Login successful. Your google account has been linked to your existing profile.", 
                             "token": generate_token(existing_user)})
            
            user, created = self.get_or_create_user(user_info)
            logger.info(f"user info: {user_info}")
            return Response({"user": UserSerializer(user).data, 
                             "message": "Login successful.", 
                             "token": generate_token(user)})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def get_or_create_user(user_info: dict):
        google_id = user_info['sub']
        user, created = User.objects.get_or_create(
            google_id=google_id,
            defaults={
                "email": user_info.get('email', ""),
                "first_name": user_info.get('given_name', ""),
                "last_name": user_info.get('family_name', ""),
            }
        )
        return user, created
    

class AvatarUploadView(APIView):
    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        file = request.FILES.get("avatar")
        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            url = upload_avatar(file)
            request.user.avatar = url
            request.user.save()
            return Response({"avatar": url})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class FollowView(APIView):
    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if request.user.id == user_id:
            return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "The user you tried to follow does not exist."}, status=status.HTTP_404_NOT_FOUND)

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            return Response({"error": f"You are already followng this user."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"You are now following {follow.following}"})


