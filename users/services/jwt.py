import jwt
from datetime import datetime, timedelta, timezone

from django.conf import settings

from ..models import User


def generate_token(user: User) -> str:
    """
    Generates a signed JWT token for the given user.

    Encodes the user's ID and token timestamps into a payload,
    then signs it using the application's secret key. The token
    expires 24 hours from the time of issuance.

    Args:
        user (User): The authenticated user for whom the token is being generated.

    Returns:
        str: A signed JWT token string valid for 24 hours.
    """
    token_issued_at = datetime.now(tz=timezone.utc)

    token_payload = {
        "user_id": user.id,                                 # Embed the user's ID for later lookup during authentication.
        "iat": token_issued_at,                         # Timestamp of when the token was issued.
        "exp": token_issued_at + timedelta(days=1)      # Token expires 24 hours after issuance.
    }

    return jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')


def decode_token(encoded_token: str) -> dict:
    """
    Decodes and verifies a signed JWT token.

    Validates the token's signature and expiry using the application's
    secret key and returns the decoded payload.

    Args:
        encoded_token (str): The JWT token string to decode.

    Returns:
        dict: The decoded token payload containing user_id, iat, and exp claims.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is malformed or the signature is invalid.
    """
    return jwt.decode(encoded_token, settings.SECRET_KEY, algorithms=['HS256'])