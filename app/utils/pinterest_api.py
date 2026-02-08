
"""
Pinterest API Utility Module
Handles OAuth 2.0 authentication and pin creation for Pinterest API v5.
"""
import requests
import base64
from urllib.parse import urlencode
from config import Config

PINTEREST_AUTH_URL = "https://www.pinterest.com/oauth/"
PINTEREST_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
PINTEREST_API_BASE = "https://api.pinterest.com/v5"


def get_auth_url():
    """
    Generate the Pinterest OAuth authorization URL.
    User must visit this URL to authorize the app.
    """
    params = {
        "client_id": Config.PINTEREST_APP_ID,
        "redirect_uri": Config.PINTEREST_REDIRECT_URI,
        "response_type": "code",
        "scope": "boards:read,boards:write,pins:read,pins:write",
        "state": "ai_business_partner"
    }
    
    auth_url = f"{PINTEREST_AUTH_URL}?{urlencode(params)}"
    return auth_url


def exchange_code_for_token(auth_code):
    """
    Exchange authorization code for access token.
    Returns access_token, refresh_token.
    """
    # Pinterest uses Basic Auth for token exchange
    credentials = f"{Config.PINTEREST_APP_ID}:{Config.PINTEREST_APP_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": Config.PINTEREST_REDIRECT_URI
    }
    
    response = requests.post(PINTEREST_TOKEN_URL, headers=headers, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        print("[Pinterest] Token exchange successful!")
        return tokens["access_token"], tokens.get("refresh_token")
    else:
        print(f"[Pinterest] Token exchange failed: {response.text}")
        return None, None


def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token."""
    credentials = f"{Config.PINTEREST_APP_ID}:{Config.PINTEREST_APP_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(PINTEREST_TOKEN_URL, headers=headers, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        return tokens["access_token"], tokens.get("refresh_token")
    else:
        print(f"[Pinterest] Token refresh failed: {response.text}")
        return None, None


def create_pin(title, description, link, image_url=None, alt_text="Digital Product"):
    """
    Create a pin on Pinterest.
    
    Args:
        title: Pin title
        description: Pin description
        link: Link to the product (e.g., Google Sheet or Etsy listing)
        image_url: URL of the image to pin (optional, uses placeholder if None)
        alt_text: Alt text for the image
    
    Returns:
        Pin ID if successful, None otherwise.
    """
    access_token = Config.PINTEREST_ACCESS_TOKEN
    board_id = Config.PINTEREST_BOARD_ID
    
    if not access_token or not board_id:
        print("[Pinterest] Missing access token or board ID. Run OAuth first.")
        return None
    
    url = f"{PINTEREST_API_BASE}/pins"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Use a placeholder image if none provided
    if not image_url:
        image_url = "https://via.placeholder.com/600x900?text=Digital+Product"
    
    data = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "link": link,
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        },
        "alt_text": alt_text
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        pin = response.json()
        pin_id = pin.get("id")
        print(f"[Pinterest] Pin created! ID: {pin_id}")
        return pin_id
    else:
        print(f"[Pinterest] Failed to create pin: {response.status_code} - {response.text}")
        return None


def get_pin_url(pin_id):
    """Generate the Pinterest pin URL."""
    return f"https://www.pinterest.com/pin/{pin_id}/"


if __name__ == "__main__":
    # Test: Generate auth URL
    auth_url = get_auth_url()
    print(f"\nVisit this URL to authorize:\n{auth_url}")
