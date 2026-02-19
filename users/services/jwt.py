from ..models import User
from datetime import datetime, timedelta, timezone
import jwt
from django.conf import settings

def generate_token(user: User) -> str:
    payload = {
        "user_id": user.id,
        "iat": datetime.now(tz=timezone.utc),
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=1)
    }
    print(f"from jwt service payload is: {payload}")
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def decode_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])