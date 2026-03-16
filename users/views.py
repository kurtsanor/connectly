from rest_framework.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import viewsets, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings

from .models import User, Follow
from .serializers import GoogleCallbackSerializer, UserSerializer, FollowSerializer
from .permissions import IsAuthenticated
from .authentication import JwtAuthentication
from .services.google_oauth import exchange_code, get_google_auth_url, get_user_info
from .services.jwt import generate_token
from .services.cloudinary import upload_avatar
from connectly.singletons.logger_singleton import LoggerSingleton
from .factories import UserFactory


# Instantiate the global logger once using the Singleton pattern for shared use across all views.
logger = LoggerSingleton().get_logger()


class UserListCreate(APIView):
    """
    APIView for retrieval and creation of users.

    GET  /users/ — Returns a list of all registered users (requires authentication).
    POST /users/ — Registers a new user account (publicly accessible).
    """

    authentication_classes = [JwtAuthentication]

    def get_permissions(self):
        """
        Returns the appropriate permission set based on the HTTP method.

        Registration (POST) is publicly accessible; all other methods require authentication.
        """
        if self.request.method == 'POST':   # Registration endpoint is publicly accessible.
            return []
        # Require authentication for any other requests.
        return [IsAuthenticated()]

    def get(self, request):
        """
        Retrieves and returns a serialized list of all registered users.
        """
        all_users = User.objects.all()
        user_serializer = UserSerializer(all_users, many=True)  # many=True tells DRF to serialize a list of objects.
        return Response(user_serializer.data)

    def post(self, request):
        """
        Registers a new user with a securely hashed password.

        Validates that both username and password are provided, then hashes
        the password before saving the new user to the database.
        """
        submitted_username = request.data.get('username')
        submitted_password = request.data.get('password')

        # Ensure both required fields are present before proceeding.
        if not submitted_username or not submitted_password:
            raise serializers.ValidationError({
                "username": "This field is required",
                "password": "This field is required"
            })

        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        validated_data = user_serializer.validated_data

        # delegate the creation to the User Factory to handle hashing and additional logic
        try:
            new_user = UserFactory.create_user(
                username=submitted_username,
                password=submitted_password,
                email=validated_data.get('email'),
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                role=validated_data.get('role')
            )

            response_serializer = UserSerializer(new_user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as user_creation_error:
            raise ValidationError(detail=str(user_creation_error))


class LoginView(APIView):
    """
    Handles standard username and password authentication.

    POST /login/ — Validates credentials and returns a JWT token on success.
    """

    def post(self, request):
        """
        Authenticates a user and issues a JWT token upon successful login.

        Verifies that the provided username exists and that the password matches
        the stored hash. Returns a JWT token if credentials are valid.
        """
        submitted_username = request.data.get('username')
        submitted_password = request.data.get('password')

        # Reject requests that are missing required login fields.
        if not submitted_username or not submitted_password:
            raise serializers.ValidationError({
                "username": "This field is required",
                "password": "This field is required"
            })

        try:
            matched_user = User.objects.get(username=submitted_username)
        except User.DoesNotExist:
            # Return a generic error to avoid revealing whether the username exists.
            return Response({'error': "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(submitted_password, matched_user.password):
            return Response({'error': "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate and return a signed JWT token for the authenticated user.
        auth_token = generate_token(matched_user)
        return Response({"message": "Login successful", 'token': auth_token}, status=status.HTTP_200_OK)


class GoogleAuthUrlView(APIView):
    """
    Provides the Google OAuth2 authorization URL for initiating the login flow.

    GET /auth/google/ — Returns the URL the client should redirect the user to.
    """

    def get(self, request):
        """
        Returns the Google OAuth2 authorization URL.
        """
        google_auth_url = get_google_auth_url()
        return Response({"auth_url": google_auth_url})


class GoogleCallbackView(APIView):
    """
    Receives the authorization code returned by Google after user consent.

    GET /auth/google/callback/ — Captures the authorization code from Google's redirect.
    """

    def get(self, request):
        """
        Extracts and returns the authorization code from the Google OAuth2 callback.
        """
        authorization_code = request.query_params.get('code')

        if not authorization_code:
            return Response({"error": "Authorization code not found."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"Received Google authorization code: {authorization_code}")
        return Response({"code": authorization_code})


class GoogleLoginView(APIView):
    """
    Completes the Google OAuth2 login flow by exchanging an authorization code
    for user information and issuing a JWT token.

    POST /auth/google/login/ — Accepts the authorization code and returns a JWT token.
    """

    def post(self, request):
        """
        Exchanges a Google authorization code for user info and authenticates the user.

        If the Google email matches an existing account without a linked Google ID,
        the Google account is linked to that existing profile. Otherwise, a new
        user account is retrieved or created using the Google ID.
        """
        code_serializer = GoogleCallbackSerializer(data=request.data)
        code_serializer.is_valid(raise_exception=True)

        try:
            # Exchange the authorization code for OAuth tokens, then fetch the user's Google profile.
            oauth_tokens = exchange_code(code_serializer.validated_data["code"])
            google_user_info = get_user_info(oauth_tokens["access_token"])

            google_email = google_user_info.get('email')

            # If the email matches an existing account with no Google ID, link the accounts.
            existing_user = User.objects.filter(email=google_email).first()

            if existing_user and not existing_user.google_id:
                existing_user.google_id = google_user_info.get('sub')  # 'sub' is Google's unique user identifier.
                existing_user.save()
                return Response({
                    "user":    UserSerializer(existing_user).data,
                    "message": "Login successful. Your Google account has been linked to your existing profile.",
                    "token":   generate_token(existing_user)
                })

            authenticated_user, account_created = self.get_or_create_user(google_user_info)
            logger.info(f"Google user info retrieved: {google_user_info}")

            return Response({
                "user":    UserSerializer(authenticated_user).data,
                "message": "Login successful.",
                "token":   generate_token(authenticated_user)
            })

        except Exception as google_login_error:
            return Response({"error": str(google_login_error)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_or_create_user(google_user_info: dict):
        """
        Retrieves an existing user by Google ID or creates a new one if not found.

        Uses 'sub' as the unique Google identifier to look up or create the user record.
        Default field values are pulled from the Google profile if available.
        """
        google_id = google_user_info['sub']     # 'sub' is the stable, unique ID Google assigns each user.

        user_account, account_created = User.objects.get_or_create(
            google_id=google_id,
            defaults={
                "email":      google_user_info.get('email', ""),
                "first_name": google_user_info.get('given_name', ""),
                "last_name":  google_user_info.get('family_name', ""),
            }
        )
        return user_account, account_created


class AvatarUploadView(APIView):
    """
    Handles uploading and updating the authenticated user's profile avatar.

    POST /users/avatar/ — Uploads an image file to Cloudinary and saves
                          the resulting URL on the user's profile record.
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Uploads an avatar image to Cloudinary and saves the URL to the user's profile.

        Expects a multipart form file with the key 'avatar'. On success, the user's
        avatar field is updated with the Cloudinary-hosted image URL.
        """
        uploaded_file = request.FILES.get("avatar")

        if not uploaded_file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Upload the file to Cloudinary and retrieve the hosted image URL.
            cloudinary_url = upload_avatar(uploaded_file)
            request.user.avatar = cloudinary_url
            request.user.save()
            return Response({"avatar": cloudinary_url})

        except Exception as upload_error:
            return Response({"error": str(upload_error)}, status=status.HTTP_400_BAD_REQUEST)


class FollowView(APIView):
    """
    Manages follow relationships between users on the Connectly platform.

    POST /users/<user_id>/follow/ — Creates a follow relationship between the
                                    authenticated user and the specified target user.
    """

    authentication_classes = [JwtAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        """
        Creates a follow relationship from the authenticated user to the target user.

        Prevents users from following themselves and handles duplicate follow attempts
        with a descriptive error response.
        """
        # Prevent a user from following their own account.
        if request.user.id == user_id:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "The user you tried to follow does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to create the follow record; skip creation if it already exists.
        follow_record, follow_created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )

        if not follow_created:
            return Response({"error": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": f"You are now following {follow_record.following}."})