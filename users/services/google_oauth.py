import requests
from urllib.parse import urlencode
from rest_framework.exceptions import AuthenticationFailed

from connectly import settings


# Google OAuth2 endpoint URLs.
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_google_auth_url() -> str:
    """
    Builds and returns the Google OAuth2 authorization URL.

    Constructs the URL with the required query parameters so the client
    can redirect the user to Google's consent screen.

    Returns:
        str: The full Google authorization URL including query parameters.
    """
    auth_params = {
        "client_id":     settings.GOOGLE_CLIENT_ID,
        "redirect_uri":  settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",                        # Request an authorization code in return.
        "scope":         "openid email profile",        # Request access to the user's basic profile info.
        "access_type":   "offline",                     # Request a refresh token for long-lived access.
        "prompt":        "consent",                     # Always show the consent screen to ensure a refresh token is issued.
    }
    encoded_params = urlencode(auth_params)
    return f"{GOOGLE_AUTH_URL}?{encoded_params}"


def exchange_code(authorization_code: str) -> dict:
    """
    Exchanges a Google authorization code for OAuth2 access and refresh tokens.

    Sends the authorization code to Google's token endpoint along with the
    app credentials to receive a token response.

    Args:
        authorization_code (str): The one-time authorization code received from Google's callback.

    Returns:
        dict: A dictionary containing the access token, refresh token, and token metadata.

    Raises:
        AuthenticationFailed: If the authorization code is expired, invalid, or already used.
    """
    token_response = requests.post(GOOGLE_TOKEN_URL, data={
        "code":          authorization_code,
        "client_id":     settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri":  settings.GOOGLE_REDIRECT_URI,
        "grant_type":    "authorization_code",          # Specify the OAuth2 grant type being used.
    })

    if token_response.status_code == 400:
        # Google returns 400 when the code is expired, already used, or malformed.
        raise AuthenticationFailed("Authorization code is expired, invalid, or already used.")

    token_response.raise_for_status()   # Raise an error for any other unexpected HTTP failure.
    return token_response.json()


def get_user_info(access_token: str) -> dict:
    """
    Retrieves the authenticated user's profile information from Google.

    Sends the access token to Google's userinfo endpoint and returns
    the user's profile data including email, name, and Google ID.

    Args:
        access_token (str): A valid Google OAuth2 access token.

    Returns:
        dict: A dictionary containing the user's Google profile data,
              including 'sub' (unique ID), 'email', 'given_name', and 'family_name'.

    Raises:
        HTTPError: If the request to Google's userinfo endpoint fails.
    """
    userinfo_response = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"}    # Pass the access token as a Bearer header.
    )
    userinfo_response.raise_for_status()
    return userinfo_response.json()