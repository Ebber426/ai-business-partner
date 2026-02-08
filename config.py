
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # V1 Configuration
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

    # V2: Etsy Configuration
    ETSY_API_KEY = os.getenv("ETSY_API_KEY")
    ETSY_API_SECRET = os.getenv("ETSY_API_SECRET")
    ETSY_REDIRECT_URI = os.getenv("ETSY_REDIRECT_URI", "http://localhost:8080/etsy/callback")
    ETSY_SHOP_ID = os.getenv("ETSY_SHOP_ID")
    ETSY_ACCESS_TOKEN = os.getenv("ETSY_ACCESS_TOKEN")
    ETSY_REFRESH_TOKEN = os.getenv("ETSY_REFRESH_TOKEN")

    # V2: Pinterest Configuration
    PINTEREST_APP_ID = os.getenv("PINTEREST_APP_ID")
    PINTEREST_APP_SECRET = os.getenv("PINTEREST_APP_SECRET")
    PINTEREST_REDIRECT_URI = os.getenv("PINTEREST_REDIRECT_URI", "http://localhost:8080/pinterest/callback")
    PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
    PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")
    PINTEREST_REFRESH_TOKEN = os.getenv("PINTEREST_REFRESH_TOKEN")

    # Validate V1 configuration
    if not GOOGLE_APPLICATION_CREDENTIALS:
        print("Warning: GOOGLE_APPLICATION_CREDENTIALS not found in .env")
    if not TELEGRAM_BOT_TOKEN:
        print("Warning: TELEGRAM_BOT_TOKEN not found in .env")
    if not GOOGLE_SHEET_ID:
        print("Warning: GOOGLE_SHEET_ID not found in .env")
