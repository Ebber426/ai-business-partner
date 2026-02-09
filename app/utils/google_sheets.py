
import gspread
import datetime
from google.oauth2.service_account import Credentials
from config import Config

# Define scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    """Authenticates and returns a gspread client."""
    creds = Credentials.from_service_account_file(
        Config.GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES
    )
    client = gspread.authorize(creds)
    return client

def get_sheet():
    """Returns the main system memory sheet."""
    client = get_client()
    try:
        sheet = client.open_by_key(Config.GOOGLE_SHEET_ID)
        return sheet
    except Exception as e:
        print(f"Error opening sheet: {e}")
        return None

def setup_tabs():
    """Ensures necessary tabs exist."""
    sheet = get_sheet()
    if not sheet:
        return

    # Map expected tabs to actual tab names in the user's sheet
    # User has: research_logs, products, uploads, revenue, daily_activity
    required_tabs = {
        "Research": "research_logs",
        "Products": "products", 
        "Activity Log": "daily_activity",
        "Revenue": "revenue"
    }
    
    existing_tabs = [ws.title for ws in sheet.worksheets()]

    for default_name, actual_name in required_tabs.items():
        # Check if either name exists
        if actual_name not in existing_tabs and default_name not in existing_tabs:
            try:
                sheet.add_worksheet(title=actual_name, rows=100, cols=10)
                ws = sheet.worksheet(actual_name)
                if "research" in actual_name.lower():
                    ws.append_row(["Timestamp", "Keyword", "Platform", "Signal", "Notes"])
                elif "products" in actual_name.lower():
                    ws.append_row(["Timestamp", "Product Name", "Type", "Link", "Status"])
                elif "activity" in actual_name.lower():
                    ws.append_row(["Timestamp", "Agent", "Action", "Result"])
                elif "revenue" in actual_name.lower():
                    ws.append_row(["Timestamp", "Source", "Amount", "Currency"])
            except Exception as e:
                print(f"Tab setup note: {e}")

def log_activity(agent_name, action, result):
    """Logs an action to the Activity Log tab."""
    sheet = get_sheet()
    if not sheet:
        return
    
    try:
        # Try user's tab name first, fallback to default
        try:
            ws = sheet.worksheet("daily_activity")
        except:
            ws = sheet.worksheet("Activity Log")
        timestamp = datetime.datetime.now().isoformat()
        ws.append_row([timestamp, agent_name, action, result])
        print(f"[{agent_name}] {action}: {result}")
    except Exception as e:
        print(f"Error logging activity: {e}")

def save_research(data):
    """Saves research data to the Research tab."""
    sheet = get_sheet()
    if not sheet:
        return

    try:
        # Try user's tab name first, fallback to default
        try:
            ws = sheet.worksheet("research_logs")
        except:
            ws = sheet.worksheet("Research")
        timestamp = datetime.datetime.now().isoformat()
        # Expecting data to be a dict or list of dicts
        if isinstance(data, list):
            for item in data:
                ws.append_row([
                    timestamp,
                    item.get("keyword", ""),
                    item.get("platform", ""),
                    item.get("signal", ""),
                    item.get("notes", "")
                ])
        elif isinstance(data, dict):
             ws.append_row([
                timestamp,
                data.get("keyword", ""),
                data.get("platform", ""),
                data.get("signal", ""),
                data.get("notes", "")
            ])
    except Exception as e:
        print(f"Error saving research: {e}")

def log_product(product_data):
    """Logs a new product to the Products tab."""
    sheet = get_sheet()
    if not sheet:
        return

    try:
        # Try user's tab name first, fallback to default
        try:
            ws = sheet.worksheet("products")
        except:
            ws = sheet.worksheet("Products")
        timestamp = datetime.datetime.now().isoformat()
        ws.append_row([
            timestamp,
            product_data.get("name", ""),
            product_data.get("type", ""),
            product_data.get("link", ""),
            product_data.get("status", "Created")
        ])
    except Exception as e:
        print(f"Error logging product: {e}")

def get_revenue():
    """Calculates total revenue."""
    sheet = get_sheet()
    if not sheet:
        return 0.0

    try:
        ws = sheet.worksheet("Revenue")
        records = ws.get_all_records()
        total = sum(float(r["Amount"]) for r in records if str(r["Amount"]).replace('.', '', 1).isdigit())
        return total
    except Exception as e:
        print(f"Error calculating revenue: {e}")
        return 0.0
