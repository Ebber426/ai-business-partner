
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

    # New schema: research_runs and research_items
    required_tabs = {
        "research_runs": ["run_id", "timestamp", "keywords_count", "status"],
        "research_items": ["run_id", "keyword", "demand_score", "product_type", "timestamp", "deleted"],
        "products": ["Timestamp", "Product Name", "Type", "Link", "Status"],
        "daily_activity": ["Timestamp", "Agent", "Action", "Result"],
        "revenue": ["Timestamp", "Source", "Amount", "Currency"]
    }
    
    existing_tabs = [ws.title for ws in sheet.worksheets()]

    for tab_name, headers in required_tabs.items():
        if tab_name not in existing_tabs:
            try:
                sheet.add_worksheet(title=tab_name, rows=100, cols=len(headers))
                ws = sheet.worksheet(tab_name)
                ws.append_row(headers)
                print(f"Created sheet: {tab_name}")
            except Exception as e:
                print(f"Tab setup note for {tab_name}: {e}")

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
        ws = sheet.worksheet("revenue")
        records = ws.get_all_records()
        total = sum(float(r["Amount"]) for r in records if str(r["Amount"]).replace('.', '', 1).isdigit())
        return total
    except Exception as e:
        print(f"Error calculating revenue: {e}")
        return 0.0

# ==================== RESEARCH RUN MANAGEMENT ====================

def create_research_run():
    """Creates a new research run and returns the run_id."""
    import uuid
    sheet = get_sheet()
    if not sheet:
        raise RuntimeError("Failed to connect to Google Sheets")
    
    try:
        ws = sheet.worksheet("research_runs")
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.datetime.now().isoformat()
        ws.append_row([run_id, timestamp, 0, "running"])
        print(f"Created research run: {run_id}")
        return run_id
    except Exception as e:
        raise RuntimeError(f"Failed to create research run: {e}") from e

def complete_research_run(run_id, keywords_count):
    """Marks a research run as complete."""
    sheet = get_sheet()
    if not sheet:
        return
    
    try:
        ws = sheet.worksheet("research_runs")
        all_values = ws.get_all_values()
        for i, row in enumerate(all_values):
            if row[0] == run_id:
                ws.update_cell(i + 1, 3, keywords_count)  # Update keywords_count
                ws.update_cell(i + 1, 4, "complete")  # Update status
                print(f"Marked run {run_id} as complete with {keywords_count} keywords")
                break
    except Exception as e:
        print(f"Error completing research run: {e}")

def save_research_items(run_id, items):
    """Saves research items for a given run."""
    sheet = get_sheet()
    if not sheet:
        raise RuntimeError("Failed to connect to Google Sheets")
    
    try:
        ws = sheet.worksheet("research_items")
        timestamp = datetime.datetime.now().isoformat()
        
        for item in items:
            ws.append_row([
                run_id,
                item.get("keyword", ""),
                item.get("demand_score", 0),
                item.get("product_type", "Unknown"),
                timestamp,
                "FALSE"  # deleted
            ])
        print(f"Saved {len(items)} items to research_items")
    except Exception as e:
        raise RuntimeError(f"Failed to save research items: {e}") from e

def get_latest_research_run():
    """Gets the latest research run with its items."""
    sheet = get_sheet()
    if not sheet:
        return {"results": []}
    
    try:
        runs_ws = sheet.worksheet("research_runs")
        runs = runs_ws.get_all_records()
        
        if not runs:
            return {"results": []}
        
        # Get latest run (last row)
        latest_run = runs[-1]
        run_id = latest_run["run_id"]
        
        # Get items for this run
        items_ws = sheet.worksheet("research_items")
        all_items = items_ws.get_all_records()
        
        # Filter by run_id and not deleted
        run_items = [
            {
                "keyword": item["keyword"],
                "signal": float(item["demand_score"]),
                "platform": item["product_type"],
                "notes": f"From run: {run_id}",
                "timestamp": item["timestamp"]
            }
            for item in all_items
            if item["run_id"] == run_id and item["deleted"] != "TRUE"
        ]
        
        return {"results": run_items, "run_id": run_id}
    except Exception as e:
        print(f"Error getting latest research run: {e}")
        return {"results": []}

def delete_research_item(keyword):
    """Marks a research item as deleted."""
    sheet = get_sheet()
    if not sheet:
        raise RuntimeError("Failed to connect to Google Sheets")
    
    try:
        ws = sheet.worksheet("research_items")
        all_values = ws.get_all_values()
        
        # Find and mark as deleted (from latest run)
        runs_ws = sheet.worksheet("research_runs")
        runs = runs_ws.get_all_records()
        if not runs:
            raise RuntimeError("No research runs found")
        
        latest_run_id = runs[-1]["run_id"]
        
        for i, row in enumerate(all_values):
            if i == 0:  # Skip header
                continue
            if row[0] == latest_run_id and row[1] == keyword and row[5] != "TRUE":
                ws.update_cell(i + 1, 6, "TRUE")  # Mark deleted
                print(f"Deleted item: {keyword}")
                return True
        
        raise RuntimeError(f"Item '{keyword}' not found in latest run")
    except Exception as e:
        raise RuntimeError(f"Failed to delete research item: {e}") from e

def delete_latest_research_run():
    """Marks all items in the latest research run as deleted."""
    sheet = get_sheet()
    if not sheet:
        raise RuntimeError("Failed to connect to Google Sheets")
    
    try:
        # Get latest run_id
        runs_ws = sheet.worksheet("research_runs")
        runs = runs_ws.get_all_records()
        if not runs:
            raise RuntimeError("No research runs found")
        
        latest_run_id = runs[-1]["run_id"]
        
        # Mark all items as deleted
        items_ws = sheet.worksheet("research_items")
        all_values = items_ws.get_all_values()
        
        deleted_count = 0
        for i, row in enumerate(all_values):
            if i == 0:  # Skip header
                continue
            if row[0] == latest_run_id and row[5] != "TRUE":
                items_ws.update_cell(i + 1, 6, "TRUE")
                deleted_count += 1
        
        print(f"Deleted {deleted_count} items from run {latest_run_id}")
        return deleted_count
    except Exception as e:
        raise RuntimeError(f"Failed to delete latest research run: {e}") from e
