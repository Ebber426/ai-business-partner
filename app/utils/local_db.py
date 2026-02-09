"""
Local SQLite Database for AI Business Partner
Replaces Google Sheets for system memory (research, activity logs, products)
"""

import sqlite3
import datetime
import uuid
from pathlib import Path
from typing import List, Dict, Optional


DB_PATH = Path(__file__).parent.parent.parent / "data" / "business_partner.db"


def get_connection():
    """Get database connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """Initialize database with schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Research runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_runs (
            run_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            keywords_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'running'
        )
    """)
    
    # Research items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            keyword TEXT NOT NULL,
            demand_score REAL DEFAULT 0,
            product_type TEXT,
            timestamp TEXT NOT NULL,
            deleted INTEGER DEFAULT 0,
            FOREIGN KEY (run_id) REFERENCES research_runs(run_id)
        )
    """)
    
    # Activity log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            agent TEXT NOT NULL,
            action TEXT NOT NULL,
            result TEXT
        )
    """)
    
    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            sheet_url TEXT,
            timestamp TEXT NOT NULL,
            status TEXT DEFAULT 'active'
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Local database initialized")


# ==================== RESEARCH RUN MANAGEMENT ====================

def create_research_run() -> str:
    """Creates a new research run and returns the run_id."""
    conn = get_connection()
    cursor = conn.cursor()
    
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO research_runs (run_id, timestamp, keywords_count, status) VALUES (?, ?, ?, ?)",
        (run_id, timestamp, 0, "running")
    )
    
    conn.commit()
    conn.close()
    
    print(f"Created research run: {run_id}")
    return run_id


def complete_research_run(run_id: str, keywords_count: int):
    """Marks a research run as complete."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE research_runs SET keywords_count = ?, status = ? WHERE run_id = ?",
        (keywords_count, "complete", run_id)
    )
    
    conn.commit()
    conn.close()
    print(f"Marked run {run_id} as complete with {keywords_count} keywords")


def save_research_items(run_id: str, items: List[Dict]):
    """Saves research items for a given run."""
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now().isoformat()
    
    for item in items:
        cursor.execute(
            """INSERT INTO research_items 
               (run_id, keyword, demand_score, product_type, timestamp, deleted) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                item.get("keyword", ""),
                item.get("demand_score", 0),
                item.get("product_type", "Unknown"),
                timestamp,
                0
            )
        )
    
    conn.commit()
    conn.close()
    print(f"Saved {len(items)} items to research_items")


def get_latest_research_run() -> Dict:
    """Gets the latest research run with its items."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get latest run
    cursor.execute(
        "SELECT * FROM research_runs ORDER BY timestamp DESC LIMIT 1"
    )
    run = cursor.fetchone()
    
    if not run:
        conn.close()
        return {"results": []}
    
    run_id = run["run_id"]
    
    # Get items for this run (not deleted)
    cursor.execute(
        """SELECT keyword, demand_score, product_type, timestamp 
           FROM research_items 
           WHERE run_id = ? AND deleted = 0""",
        (run_id,)
    )
    
    items = cursor.fetchall()
    conn.close()
    
    results = [
        {
            "keyword": item["keyword"],
            "signal": float(item["demand_score"]),
            "platform": item["product_type"],
            "notes": f"From run: {run_id}",
            "timestamp": item["timestamp"]
        }
        for item in items
    ]
    
    return {"results": results, "run_id": run_id}


def delete_research_item(keyword: str):
    """Marks a research item as deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get latest run_id
    cursor.execute(
        "SELECT run_id FROM research_runs ORDER BY timestamp DESC LIMIT 1"
    )
    run = cursor.fetchone()
    
    if not run:
        conn.close()
        raise RuntimeError("No research runs found")
    
    run_id = run["run_id"]
    
    # Mark as deleted
    cursor.execute(
        "UPDATE research_items SET deleted = 1 WHERE run_id = ? AND keyword = ? AND deleted = 0",
        (run_id, keyword)
    )
    
    if cursor.rowcount == 0:
        conn.close()
        raise RuntimeError(f"Item '{keyword}' not found in latest run")
    
    conn.commit()
    conn.close()
    print(f"Deleted item: {keyword}")


def delete_latest_research_run() -> int:
    """Marks all items in the latest research run as deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get latest run_id
    cursor.execute(
        "SELECT run_id FROM research_runs ORDER BY timestamp DESC LIMIT 1"
    )
    run = cursor.fetchone()
    
    if not run:
        conn.close()
        raise RuntimeError("No research runs found")
    
    run_id = run["run_id"]
    
    # Mark all items as deleted
    cursor.execute(
        "UPDATE research_items SET deleted = 1 WHERE run_id = ? AND deleted = 0",
        (run_id,)
    )
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"Deleted {deleted_count} items from run {run_id}")
    return deleted_count


# ==================== ACTIVITY LOG ====================

def log_activity(agent: str, action: str, result: str):
    """Logs an activity to the local database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO activity_log (timestamp, agent, action, result) VALUES (?, ?, ?, ?)",
        (timestamp, agent, action, result)
    )
    
    conn.commit()
    conn.close()


def get_activity_logs(limit: int = 100) -> List[Dict]:
    """Gets recent activity logs."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    
    logs = cursor.fetchall()
    conn.close()
    
    return [dict(log) for log in logs]


# ==================== PRODUCTS ====================

def save_product(keyword: str, sheet_url: str, status: str = "active"):
    """Saves product metadata to local database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO products (keyword, sheet_url, timestamp, status) VALUES (?, ?, ?, ?)",
        (keyword, sheet_url, timestamp, status)
    )
    
    conn.commit()
    conn.close()
    print(f"Saved product: {keyword}")


def get_all_products() -> List[Dict]:
    """Gets all products from local database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM products ORDER BY timestamp DESC"
    )
    
    products = cursor.fetchall()
    conn.close()
    
    return [
        {
            "name": p["keyword"],
            "link": p["sheet_url"],
            "timestamp": p["timestamp"],
            "status": p["status"]
        }
        for p in products
    ]
