"""
AI Business Partner - FastAPI Backend
Web-based interface replacing Telegram bot
"""

import asyncio
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.research_agent import ResearchAgent
from app.agents.creation_agent import CreationAgent
from app.utils.local_db import (
    init_db,
    log_activity,
    get_latest_research_run,
    delete_research_item,
    delete_latest_research_run,
    save_product,
    get_all_products
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Business Partner",
    description="Automated digital product business platform",
    version="2.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class TrendData(BaseModel):
    keyword: str
    platform: Optional[str] = "Multi-Source"
    signal: Optional[float] = 0
    notes: Optional[str] = ""

class CreateProductRequest(BaseModel):
    keyword: str
    platform: Optional[str] = "Web"

class PublishRequest(BaseModel):
    platform: str = "pinterest"  # "pinterest" only


# ==================== API ENDPOINTS ====================

@app.on_event("startup")
async def startup():
    """Initialize application on startup."""
    logger.info("🚀 AI Business Partner API starting...")
    init_db()
    logger.info("✅ Local database initialized")

@app.get("/api/status")
async def get_status():
    """Get system status and last activity."""
    # sheet = get_sheet() # This line is no longer needed with local_db
    last_activity = None
    
    if sheet:
        try:
            try:
                ws = sheet.worksheet("daily_activity")
            except:
                ws = sheet.worksheet("Activity Log")
            all_values = ws.get_all_values()
            if len(all_values) > 1:
                last_entry = all_values[-1]
                last_activity = {
                    "timestamp": last_entry[0],
                    "agent": last_entry[1],
                    "action": last_entry[2],
                    "result": last_entry[3] if len(last_entry) > 3 else ""
                }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
    
    return {
        "status": "online",
        "version": "2.0.0",
        "last_activity": last_activity
    }

@app.get("/api/revenue")
async def api_get_revenue():
    """Get total revenue."""
    total = get_revenue()
    return {"total": total, "currency": "USD"}


# ==================== RESEARCH ENDPOINTS ====================

@app.get("/api/research")
async def get_research():
    """Get latest research run results from Google Sheets."""
    logger.info("Fetching latest research run")
    try:
        result = get_latest_research_run()
        logger.info(f"Retrieved {len(result.get('results', []))} items from latest run")
        return result
    except Exception as e:
        logger.error(f"Research fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research/run")
async def run_research():
    """Trigger the research agent to create a new research run."""
    logger.info("Starting new research run")
    await manager.broadcast({"type": "status", "message": "Starting research..."})
    
    try:
        researcher = ResearchAgent()
        
        # Run in thread pool to not block
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, researcher.run)
        
        logger.info(f"Research complete: {len(results)} trends found")
        await manager.broadcast({
            "type": "research_complete",
            "message": f"Found {len(results)} trends",
            "count": len(results)
        })
        
        return {
            "success": True,
            "count": len(results)
        }
    except RuntimeError as e:
        # Specific error from ResearchAgent
        error_msg = str(e)
        logger.error(f"Research agent error: {error_msg}")
        await manager.broadcast({"type": "error", "message": error_msg})
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        # Unexpected error
        error_msg = f"Unexpected error during research: {str(e)}"
        logger.error(error_msg, exc_info=True)
        await manager.broadcast({"type": "error", "message": error_msg})
        raise HTTPException(status_code=500, detail=error_msg)

@app.delete("/api/research/{keyword}")
async def delete_research_keyword(keyword: str):
    """Delete a single research item from the latest run."""
    logger.info(f"Deleting research item: {keyword}")
    
    try:
        delete_research_item(keyword)
        log_activity("User", "Delete", f"Removed keyword: {keyword}")
        
        await manager.broadcast({
            "type": "research_deleted",
            "message": f"Deleted: {keyword}"
        })
        
        return {"success": True, "keyword": keyword}
    except RuntimeError as e:
        error_msg = str(e)
        logger.error(f"Delete error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error deleting item: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@app.delete("/api/research/latest")
async def clear_latest_research():
    """Clear all items from the latest research run."""
    logger.info("Clearing latest research run")
    
    try:
        deleted_count = delete_latest_research_run()
        log_activity("User", "Clear Research", f"Cleared {deleted_count} items from latest run")
        
        await manager.broadcast({
            "type": "research_cleared",
            "message": f"Cleared {deleted_count} items"
        })
        
        return {"success": True, "deleted_count": deleted_count}
    except RuntimeError as e:
        error_msg = str(e)
        logger.error(f"Clear error: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error clearing research: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


# ==================== PRODUCT ENDPOINTS ====================

@app.get("/api/products")
async def get_products():
    """Get all products from Google Sheets."""
    sheet = get_sheet()
    if not sheet:
        raise HTTPException(status_code=500, detail="Failed to connect to Google Sheets")
    
    try:
        try:
            ws = sheet.worksheet("products")
        except:
            ws = sheet.worksheet("Products")
        
        records = ws.get_all_records()
        return {"products": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products/create")
async def create_product(request: CreateProductRequest):
    """Create a new product from a trend keyword."""
    logger.info(f"Product creation requested for: {request.keyword}")
    await manager.broadcast({"type": "status", "message": f"Creating product: {request.keyword}"})
    
    try:
        creator = CreationAgent()
        trend_data = {
            "keyword": request.keyword,
            "platform": request.platform
        }
        
        loop = asyncio.get_event_loop()
        link = await loop.run_in_executor(None, creator.run, trend_data)
        
        # CreationAgent now raises RuntimeError on failure, so if we get here it succeeded
        logger.info(f"Product created successfully: {link}")
        await manager.broadcast({
            "type": "product_created",
            "message": f"Product created: {request.keyword}",
            "link": link
        })
        return {"success": True, "link": link}
            
    except RuntimeError as e:
        # Specific error from CreationAgent
        error_msg = str(e)
        logger.error(f"Creation agent error: {error_msg}")
        await manager.broadcast({"type": "error", "message": error_msg})
        raise HTTPException(status_code=500, detail=error_msg)
        
    except Exception as e:
        # Unexpected error
        error_msg = f"Unexpected error creating product: {str(e)}"
        logger.error(error_msg, exc_info=True)
        await manager.broadcast({"type": "error", "message": error_msg})
        raise HTTPException(status_code=500, detail=error_msg)


# ==================== PUBLISHING ENDPOINTS ====================

@app.post("/api/publish")
async def publish_product(request: PublishRequest):
    """Publish product to Pinterest for marketing automation."""
    await manager.broadcast({"type": "status", "message": f"Publishing to {request.platform}..."})
    
    try:
        publisher = PublishingAgent()
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, publisher.run, request.platform)
        
        await manager.broadcast({
            "type": "publish_complete",
            "message": f"Publishing complete",
            "results": results
        })
        
        return results
        
    except Exception as e:
        logger.error(f"Publishing error: {e}")
        await manager.broadcast({"type": "error", "message": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ACTIVITY LOG ====================

@app.get("/api/activity")
async def get_activity(limit: int = 50):
    """Get activity log."""
    sheet = get_sheet()
    if not sheet:
        raise HTTPException(status_code=500, detail="Failed to connect to Google Sheets")
    
    try:
        try:
            ws = sheet.worksheet("daily_activity")
        except:
            ws = sheet.worksheet("Activity Log")
        
        all_values = ws.get_all_values()
        
        if len(all_values) <= 1:
            return {"activities": []}
        
        # Skip header, get last N entries
        entries = all_values[1:][-limit:]
        activities = [
            {
                "timestamp": row[0],
                "agent": row[1],
                "action": row[2],
                "result": row[3] if len(row) > 3 else ""
            }
            for row in reversed(entries)  # Most recent first
        ]
        
        return {"activities": activities}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WEBSOCKET ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await manager.connect(websocket)
    try:
        await websocket.send_json({"type": "connected", "message": "Connected to AI Business Partner"})
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    print("🤖 AI Business Partner Web API")
    print("📡 Starting server at http://localhost:8000")
    print("📖 API docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
