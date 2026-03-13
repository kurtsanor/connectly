import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

from .models import User


class JwtAuthentication(BaseAuthentication):
    """
    Custom DRF authentication class that validates JWT Bearer tokens.

    Extracts the token from the Authorization header, decodes and verifies
    it using the application's secret key, and returns the matching user.
    Returns None if no token is present, allowing other authenticators to proceed.
    """

    def authenticate(self, request):
        """
        Authenticates the incoming request using a JWT Bearer token.

        Reads the Authorization header, validates the token's signature and
        expiry, then retrieves the corresponding user from the database.

        Args:
            request (Request): The incoming HTTP request containing the Authorization header.

        Returns:
            tuple: A (User, token) pair if authentication succeeds.
            None: If no Authorization header is present, allowing unauthenticated access.

        Raises:
            AuthenticationFailed: If the token is expired, invalid, or the user does not exist.
        """
        auth_header = request.headers.get('Authorization')

        # Return None if no Authorization header is present, so DRF can
        # fall through to the next authenticator or treat the request as anonymous.
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        # Extract the token value after the 'Bearer ' prefix.
        bearer_token = auth_header.split(' ')[1]

        try:
            # Decode and verify the token using the app's secret key and expected algorithm.
            token_payload = jwt.decode(bearer_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        try:
            # Look up the user identified by the token's embedded user_id claim.
            authenticated_user = User.objects.get(id=token_payload['user_id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')

        return (authenticated_user, bearer_token)