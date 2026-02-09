
"""
Publishing Agent
Publishes products to Pinterest for marketing automation.
Users manually upload products to their shop and the app downloads the created files.
"""
from app.utils.google_sheets import get_sheet, log_activity
from app.utils.pinterest_api import create_pin, get_pin_url
from config import Config


class PublishingAgent:
    def __init__(self):
        self.name = "Publishing Agent"

    def run(self, platform="pinterest"):
        """
        Publish the most recent unpublished product to Pinterest.
        
        Args:
            platform: "pinterest" (default)
        
        Returns:
            Dictionary with publish results.
        """
        log_activity(self.name, "Start", f"Publishing to Pinterest")
        
        # Get unpublished product from sheet
        product = self.get_unpublished_product()
        
        if not product:
            log_activity(self.name, "Warning", "No unpublished products found")
            return {"success": False, "message": "No unpublished products found"}
        
        results = {
            "product_name": product["name"],
            "pinterest": None
        }
        
        # Publish to Pinterest
        pinterest_result = self.publish_to_pinterest(product)
        results["pinterest"] = pinterest_result
        
        # Update product status in sheet
        self.update_product_status(product, results)
        
        log_activity(self.name, "Complete", f"Published {product['name']} to Pinterest")
        return results

    def get_unpublished_product(self):
        """Get the most recent product with status 'Created'."""
        sheet = get_sheet()
        if not sheet:
            return None
        
        try:
            ws = sheet.worksheet("Products")
            records = ws.get_all_records()
            
            # Find products with status "Created"
            for record in reversed(records):  # Most recent first
                if record.get("Status") == "Created":
                    return {
                        "name": record.get("Product Name"),
                        "type": record.get("Type"),
                        "link": record.get("Link"),
                        "timestamp": record.get("Timestamp"),
                        "row": records.index(record) + 2  # +2 for header and 0-index
                    }
            return None
        except Exception as e:
            print(f"[Publishing] Error getting product: {e}")
            return None

    def publish_to_pinterest(self, product):
        """
        Create a pin on Pinterest.
        """
        if not Config.PINTEREST_ACCESS_TOKEN:
            return {"success": False, "error": "Pinterest not authenticated"}
        
        try:
            title = product['name']
            description = f"""
🎯 {product['name']}

Get organized with this stunning {product['type']} template!

✨ Features:
• Clean, professional design
• Easy to customize
• Digital download

📎 Click the link to get yours!

#planner #productivity #organization #digitalplanner #{product['type'].lower().replace(' ', '')}
            """.strip()
            
            pin_id = create_pin(
                title=title,
                description=description,
                link=product['link'],
                image_url=None  # Will use placeholder
            )
            
            if pin_id:
                return {
                    "success": True,
                    "pin_id": pin_id,
                    "url": get_pin_url(pin_id)
                }
            else:
                return {"success": False, "error": "Failed to create pin"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_product_status(self, product, results):
        """Update the product status in the Google Sheet."""
        sheet = get_sheet()
        if not sheet:
            return
        
        try:
            ws = sheet.worksheet("Products")
            
            # Determine new status
            pinterest_ok = results.get("pinterest", {}).get("success", False)
            
            if pinterest_ok:
                new_status = "Published (Pinterest)"
            else:
                new_status = "Publish Failed"
            
            # Update status cell (column E, assuming Status is column 5)
            ws.update_cell(product["row"], 5, new_status)
            
        except Exception as e:
            print(f"[Publishing] Error updating status: {e}")


if __name__ == "__main__":
    agent = PublishingAgent()
    result = agent.run("pinterest")
    print(result)
