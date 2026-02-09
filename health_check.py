# Health Check Script
# Validates environment configuration and API connectivity

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_status(name: str, status: str, details: str = ""):
    """Print a status line."""
    icon = "✅" if status == "OK" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {name}: {status}")
    if details:
        print(f"   └─ {details}")


def check_env_variables():
    """Check all required environment variables."""
    print_header("ENVIRONMENT VARIABLES")
    
    load_dotenv()
    
    required = {
        "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "GOOGLE_SHEET_ID": os.getenv("GOOGLE_SHEET_ID"),
    }
    
    optional = {
        "REDDIT_CLIENT_ID": os.getenv("REDDIT_CLIENT_ID"),
        "REDDIT_CLIENT_SECRET": os.getenv("REDDIT_CLIENT_SECRET"),
        "PINTEREST_APP_ID": os.getenv("PINTEREST_APP_ID"),
    }
    
    all_ok = True
    
    print("\n[Required]")
    for name, value in required.items():
        if value and not value.startswith("your_"):
            # Mask sensitive values
            masked = value[:8] + "..." if len(value) > 10 else "***"
            print_status(name, "OK", f"Set to: {masked}")
        else:
            print_status(name, "FAIL", "Not configured")
            all_ok = False
    
    print("\n[Optional]")
    for name, value in optional.items():
        if value and not value.startswith("your_"):
            print_status(name, "OK", "Configured")
        else:
            print_status(name, "SKIP", "Not configured (optional)")
    
    return all_ok


def check_credentials_file():
    """Check if credentials.json exists."""
    print_header("GOOGLE SERVICE ACCOUNT")
    
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    
    if os.path.exists(creds_path):
        print_status("credentials.json", "OK", f"Found at: {creds_path}")
        
        # Try to read and validate
        try:
            import json
            with open(creds_path, 'r') as f:
                creds = json.load(f)
            
            email = creds.get("client_email", "")
            if email:
                print_status("Service Account Email", "OK", email)
                print(f"\n   📋 Share your Google Sheet with this email!")
            else:
                print_status("Service Account Email", "FAIL", "Not found in credentials")
                return False
                
        except json.JSONDecodeError:
            print_status("Credentials Format", "FAIL", "Invalid JSON")
            return False
            
        return True
    else:
        print_status("credentials.json", "FAIL", f"Not found at: {creds_path}")
        return False


def check_google_sheets():
    """Test Google Sheets connectivity."""
    print_header("GOOGLE SHEETS CONNECTION")
    
    try:
        from app.utils.google_sheets import get_sheet, get_client
        
        client = get_client()
        if client:
            print_status("gspread Client", "OK", "Authenticated")
        else:
            print_status("gspread Client", "FAIL", "Could not authenticate")
            return False
        
        sheet = get_sheet()
        if sheet:
            print_status("System Memory Sheet", "OK", f"Title: {sheet.title}")
            
            # Check tabs
            tabs = [ws.title for ws in sheet.worksheets()]
            print(f"   └─ Tabs: {', '.join(tabs)}")
            return True
        else:
            print_status("System Memory Sheet", "FAIL", "Could not open sheet")
            print("   └─ Check GOOGLE_SHEET_ID (should be the ID from the sheet URL)")
            return False
            
    except Exception as e:
        print_status("Google Sheets", "FAIL", str(e))
        return False


def check_telegram():
    """Test Telegram bot token validity."""
    print_header("TELEGRAM BOT")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token or token == "your_telegram_bot_token":
        print_status("Bot Token", "FAIL", "Not configured")
        return False
    
    try:
        import requests
        response = requests.get(
            f"https://api.telegram.org/bot{token}/getMe",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print_status("Bot Token", "OK", "Valid")
                print_status("Bot Username", "OK", f"@{bot_info.get('username', 'unknown')}")
                return True
        
        print_status("Bot Token", "FAIL", "Invalid or expired")
        return False
        
    except Exception as e:
        print_status("Telegram API", "FAIL", str(e))
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print_header("DEPENDENCIES")
    
    packages = [
        ("gspread", "Google Sheets"),
        ("google.oauth2.service_account", "Google Auth"),
        ("telegram", "Telegram Bot"),
        ("pytrends.request", "Google Trends"),
        ("dotenv", "Environment Variables"),
    ]
    
    optional_packages = [
        ("praw", "Reddit API"),
        ("bs4", "BeautifulSoup"),
        ("fake_useragent", "User Agent Rotation"),
    ]
    
    all_ok = True
    
    print("\n[Required]")
    for package, name in packages:
        try:
            __import__(package)
            print_status(name, "OK")
        except ImportError:
            print_status(name, "FAIL", f"Missing: pip install {package.split('.')[0]}")
            all_ok = False
    
    print("\n[Optional]")
    for package, name in optional_packages:
        try:
            __import__(package)
            print_status(name, "OK")
        except ImportError:
            print_status(name, "SKIP", "Not installed")
    
    return all_ok


def run_health_check():
    """Run all health checks."""
    print("\n" + "🏥" * 30)
    print("  AI BUSINESS PARTNER - HEALTH CHECK")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🏥" * 30)
    
    results = {
        "Environment Variables": check_env_variables(),
        "Credentials File": check_credentials_file(),
        "Dependencies": check_dependencies(),
        "Telegram Bot": check_telegram(),
        "Google Sheets": check_google_sheets(),
    }
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, status in results.items():
        print_status(name, "OK" if status else "FAIL")
    
    print("\n" + "-" * 40)
    
    if passed == total:
        print("✅ All checks passed! Environment is ready.")
        print("\n💡 Next steps:")
        print("   1. Run: python orchestrator.py")
        print("   2. Open Telegram and send /start to your bot")
        print("   3. Send /run to trigger research + creation")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed. Please fix issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_health_check())
