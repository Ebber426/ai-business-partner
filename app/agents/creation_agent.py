
import gspread
from app.utils.google_sheets import get_client, log_product, log_activity

class CreationAgent:
    def __init__(self):
        self.name = "Creation Agent"
        self.client = get_client()

    def run(self, trend_data):
        """Creates a product based on the trend data."""
        keyword = trend_data.get("keyword", "Untitled Product")
        print(f"[{self.name}] Starting product creation for: {keyword}")
        log_activity(self.name, "Start", f"Creating product for: {keyword}")

        try:
            # Create a new spreadsheet
            sheet_name = f"{keyword.title()} - {trend_data.get('platform', 'MVP')}"
            print(f"[{self.name}] Creating spreadsheet: {sheet_name}")
            sh = self.client.create(sheet_name)
            print(f"[{self.name}] Spreadsheet created successfully")
            
            # Apply template based on keyword
            if "planner" in keyword.lower():
                print(f"[{self.name}] Applying planner template")
                self.create_planner_template(sh)
                type_ = "Planner"
            elif "budget" in keyword.lower() or "finance" in keyword.lower():
                print(f"[{self.name}] Applying budget template")
                self.create_budget_template(sh)
                type_ = "Tracker"
            else:
                print(f"[{self.name}] Applying generic template")
                self.create_generic_template(sh)
                type_ = "Generic"

            # Share the sheet
            print(f"[{self.name}] Sharing sheet publicly")
            sh.share(None, perm_type='anyone', role='reader')
            link = sh.url
            print(f"[{self.name}] Sheet URL: {link}")

            # Log success
            product_data = {
                "name": sheet_name,
                "type": type_,
                "link": link,
                "status": "Created"
            }
            log_product(product_data)
            log_activity(self.name, "Success", f"Created {sheet_name}")
            print(f"[{self.name}] ✅ Product creation complete!")
            return link

        except Exception as e:
            error_msg = f"Failed to create product '{keyword}': {str(e)}"
            print(f"[{self.name}] ❌ {error_msg}")
            log_activity(self.name, "Error", error_msg)
            # Raise exception with details instead of returning None
            raise RuntimeError(error_msg) from e

    def create_planner_template(self, sh):
        """Creates a Daily Planner layout."""
        ws = sh.sheet1
        ws.update_title("Daily Planner")
        
        # Header
        ws.update("A1:B1", [["Daily Planner", "Date: ___________"]])
        ws.format("A1:B1", {"textFormat": {"bold": True, "fontSize": 14}})
        
        # Time slots
        times = [[f"{h}:00"] for h in range(6, 22)]
        ws.update("A3", [["Time", "Task", "Notes"]] + [t + ["", ""] for t in times])
        
        # Formatting
        ws.format("A3:C3", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}})
        # Set column widths
        # set_column_width is not directly available in gspread on worksheet object in older versions, 
        # but newer versions might support it. Safest is generic update or just raw data.
        # Minimal MVP: Just data.

    def create_budget_template(self, sh):
        """Creates a Budget Tracker layout."""
        ws = sh.sheet1
        ws.update_title("Budget Tracker")
        
        ws.update("A1", [["Monthly Budget Tracker"]])
        ws.format("A1", {"textFormat": {"bold": True, "fontSize": 14}})
        
        ws.update("A3:B3", [["Income Source", "Amount"]])
        ws.update("A4", [["Salary", 0], ["Side Hustle", 0], ["Total", "=SUM(B4:B5)"]])
        
        ws.update("D3:G3", [["Expense Category", "Planned", "Actual", "Difference"]])
        ws.update("D4", [["Rent", 1000, 1000, "=E4-F4"], ["Groceries", 300, 0, "=E5-F5"]])

        ws.format("A3:B3", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.9, "green": 0.95, "blue": 0.9}})
        ws.format("D3:G3", {"textFormat": {"bold": True}, "backgroundColor": {"red": 0.95, "green": 0.9, "blue": 0.9}})

    def create_generic_template(self, sh):
        """Creates a generic template."""
        ws = sh.sheet1
        ws.update_title("Template")
        ws.update("A1:B1", [["Title", "Description"]])

if __name__ == "__main__":
    # Test
    agent = CreationAgent()
    agent.run({"keyword": "Test Planner", "platform": "Debug"})
