
"""
Etsy API Utility Module
Handles OAuth 2.0 authentication and listing creation for Etsy Open API v3.
"""
import os
import requests
import hashlib
import base64
import secrets
from urllib.parse import urlencode
from config import Config

ETSY_AUTH_URL = "https://www.etsy.com/oauth/connect"
ETSY_TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
ETSY_API_BASE = "https://openapi.etsy.com/v3"


def generate_pkce_pair():
    """Generate PKCE code verifier and challenge for OAuth."""
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")
    return code_verifier, code_challenge


def get_auth_url():
    """
    Generate the Etsy OAuth authorization URL.
    User must visit this URL to authorize the app.
    """
    code_verifier, code_challenge = generate_pkce_pair()
    
    params = {
        "response_type": "code",
        "client_id": Config.ETSY_API_KEY,
        "redirect_uri": Config.ETSY_REDIRECT_URI,
        "scope": "listings_w listings_r shops_r",
        "state": secrets.token_urlsafe(16),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    
    auth_url = f"{ETSY_AUTH_URL}?{urlencode(params)}"
    
    # Store verifier for token exchange (in production, use secure storage)
    print(f"[Etsy] PKCE Code Verifier (save this): {code_verifier}")
    
    return auth_url, code_verifier


def exchange_code_for_token(auth_code, code_verifier):
    """
    Exchange authorization code for access token.
    Returns access_token, refresh_token.
    """
    data = {
        "grant_type": "authorization_code",
        "client_id": Config.ETSY_API_KEY,
        "redirect_uri": Config.ETSY_REDIRECT_URI,
        "code": auth_code,
        "code_verifier": code_verifier
    }
    
    response = requests.post(ETSY_TOKEN_URL, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        print("[Etsy] Token exchange successful!")
        print(f"[Etsy] Access Token: {tokens['access_token'][:20]}...")
        return tokens["access_token"], tokens["refresh_token"]
    else:
        print(f"[Etsy] Token exchange failed: {response.text}")
        return None, None


def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token."""
    data = {
        "grant_type": "refresh_token",
        "client_id": Config.ETSY_API_KEY,
        "refresh_token": refresh_token
    }
    
    response = requests.post(ETSY_TOKEN_URL, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        return tokens["access_token"], tokens["refresh_token"]
    else:
        print(f"[Etsy] Token refresh failed: {response.text}")
        return None, None


def create_draft_listing(title, description, price_cents, quantity=1, taxonomy_id=1):
    """
    Create a draft listing on Etsy.
    
    Args:
        title: Listing title
        description: Listing description
        price_cents: Price in cents (e.g., 999 for $9.99)
        quantity: Number of items available
        taxonomy_id: Etsy category ID (default 1 for testing)
    
    Returns:
        Listing ID if successful, None otherwise.
    """
    access_token = Config.ETSY_ACCESS_TOKEN
    shop_id = Config.ETSY_SHOP_ID
    
    if not access_token or not shop_id:
        print("[Etsy] Missing access token or shop ID. Run OAuth first.")
        return None
    
    url = f"{ETSY_API_BASE}/application/shops/{shop_id}/listings"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-api-key": Config.ETSY_API_KEY,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "title": title,
        "description": description,
        "price": price_cents / 100,  # Convert to dollars
        "quantity": quantity,
        "taxonomy_id": taxonomy_id,
        "who_made": "i_did",
        "when_made": "made_to_order",
        "is_supply": False,
        "type": "download",  # Digital product
        "state": "draft"  # Create as draft for safety
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code in [200, 201]:
        listing = response.json()
        listing_id = listing.get("listing_id")
        print(f"[Etsy] Draft listing created! ID: {listing_id}")
        return listing_id
    else:
        print(f"[Etsy] Failed to create listing: {response.status_code} - {response.text}")
        return None


def get_listing_url(listing_id):
    """Generate the Etsy listing URL."""
    return f"https://www.etsy.com/listing/{listing_id}"


if __name__ == "__main__":
    # Test: Generate auth URL
    auth_url, verifier = get_auth_url()
    print(f"\nVisit this URL to authorize:\n{auth_url}")
