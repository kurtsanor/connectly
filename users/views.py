from django.shortcuts import render
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer
from .permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
from .authentication import JwtAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from datetime import datetime, timedelta
from django.conf import settings

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
        
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.now() + timedelta(days=1)
        }, settings.SECRET_KEY, algorithm='HS256')

        return Response({'token': token})
        

