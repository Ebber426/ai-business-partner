
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Core Configuration
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

    # V2: Pinterest Configuration
    PINTEREST_APP_ID = os.getenv("PINTEREST_APP_ID")
    PINTEREST_APP_SECRET = os.getenv("PINTEREST_APP_SECRET")
    PINTEREST_REDIRECT_URI = os.getenv("PINTEREST_REDIRECT_URI", "http://localhost:8080/pinterest/callback")
    PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
    PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")
    PINTEREST_REFRESH_TOKEN = os.getenv("PINTEREST_REFRESH_TOKEN")

    # Validate configuration
    if not GOOGLE_APPLICATION_CREDENTIALS:
        print("Warning: GOOGLE_APPLICATION_CREDENTIALS not found in .env")
    if not GOOGLE_SHEET_ID:
        print("Warning: GOOGLE_SHEET_ID not found in .env")

