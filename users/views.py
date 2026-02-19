from django.shortcuts import render
from rest_framework import viewsets, status
from .models import User
from .serializers import GoogleCallbackSerializer, UserSerializer
from .permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
from .authentication import JwtAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from .services.google_oauth import exchange_code, get_google_auth_url, get_user_info
from connectly.singletons.logger_singleton import LoggerSingleton
from .services.jwt import generate_token

logger = LoggerSingleton().get_logger()

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes=[JwtAuthentication]

    def get_permissions(self):
        if self.action == 'create':  # register is public
            return []
        return [IsAuthenticated()]

    # registering a user
    def perform_create(self, serializer):
        data = serializer.validated_data
        
        hashed_password = make_password(data.get('password'))

        instance = User.objects.create(
            username=data.get('username'),
            email=data.get('email'),
            password=hashed_password,
         )
        serializer.instance = instance

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({'error': "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = generate_token(user)

        return Response({'token': token})
    
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
            user, created = self.upsert_user(user_info)
            logger.info(f"user info: {user_info}")
            return Response({"user": UserSerializer(user).data, 
                             "created": created, 
                             "token": generate_token(user)})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def upsert_user(user_info: dict):
        google_id = user_info['sub']
        user, created = User.objects.update_or_create(
            google_id=google_id,
            defaults={
                "email": user_info.get('email', ""),
                "first_name": user_info.get('given_name', ""),
                "last_name": user_info.get('family_name', ""),
            }
        )
        return user, created



