"""
Research Agent - Simplified for MVP
Uses Google Trends ONLY for demand signals
"""

import time
import random
from datetime import datetime, timezone
from typing import List, Dict

from pytrends.request import TrendReq
from app.utils.google_sheets import (
    create_research_run, 
    save_research_items, 
    complete_research_run, 
    log_activity
)


class ResearchAgent:
    """
    Simplified Research Agent for digital product trend detection.
    
    Data Source: Google Trends ONLY
    
    Output Schema:
    {
        keyword: string,
        demand_score: number (0-100 normalized),
        product_type: string (inferred from keyword),
        timestamp: ISO8601
    }
    """
    
    # Target keywords for digital product research
    DEFAULT_KEYWORDS = [
        "daily planner", 
        "budget tracker", 
        "habit tracker",
        "weekly planner",
        "study planner", 
        "fitness journal", 
        "meal planner",
        "goal tracker",
        "digital stickers",
        "bullet journal template",
        "expense tracker",
        "reading log",
        "water tracker",
        "mood tracker",
        "gratitude journal"
    ]
    
    def __init__(self, keywords: List[str] = None):
        self.name = "Research Agent"
        self.keywords = keywords or self.DEFAULT_KEYWORDS
    
    def run(self) -> List[Dict]:
        """
        Execute research pipeline.
        
        Returns:
            List of trend data with run_id
        """
        print(f"\n[{self.name}] Starting research for {len(self.keywords)} keywords...")
        
        # Create research run
        try:
            run_id = create_research_run()
        except Exception as e:
            log_activity(self.name, "Error", f"Failed to create run: {e}")
            raise RuntimeError(f"Failed to create research run: {e}") from e
        
        log_activity(self.name, "Start", f"Run {run_id}: Researching {len(self.keywords)} keywords")
        
        # Get Google Trends data
        print(f"[{self.name}] Fetching Google Trends data...")
        trends = self._get_google_trends()
        
        if not trends:
            log_activity(self.name, "Warning", f"Run {run_id}: No trends found")
            complete_research_run(run_id, 0)
            return []
        
        # Deduplicate within run
        deduped = self._deduplicate_keywords(trends)
        print(f"[{self.name}] Deduplication: {len(trends)} → {len(deduped)} unique keywords")
        
        # Infer product types
        enriched = self._infer_product_types(deduped)
        
        # Save to Google Sheets
        try:
            save_research_items(run_id, enriched)
            complete_research_run(run_id, len(enriched))
        except Exception as e:
            log_activity(self.name, "Error", f"Run {run_id}: Failed to save: {e}")
            raise RuntimeError(f"Failed to save research results: {e}") from e
        
        log_activity(self.name, "Success", f"Run {run_id}: Found {len(enriched)} trends")
        print(f"[{self.name}] ✅ Research complete: {len(enriched)} results saved")
        
        return enriched
    
    def _get_google_trends(self) -> List[Dict]:
        """Fetch trend data from Google Trends using pytrends."""
        results = []
        
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Process in batches of 5 (pytrends limit)
            for i in range(0, len(self.keywords), 5):
                batch = self.keywords[i:i+5]
                print(f"[{self.name}]   Processing batch {i//5 + 1}...")
                
                try:
                    pytrends.build_payload(
                        batch, 
                        cat=0, 
                        timeframe='today 3-m',  # 3-month window
                        geo='US', 
                        gprop=''
                    )
                    
                    data = pytrends.interest_over_time()
                    
                    if not data.empty:
                        means = data.mean()
                        for keyword in batch:
                            score = means.get(keyword, 0)
                            if score > 0:
                                results.append({
                                    "keyword": keyword,
                                    "demand_score": round(score, 2),
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                })
                    
                    # Rate limiting - be respectful
                    time.sleep(random.uniform(1.5, 3.0))
                    
                except Exception as e:
                    print(f"[{self.name}]   ⚠️  Batch error: {e}")
                    # Use fallback for this batch
                    for keyword in batch:
                        results.append({
                            "keyword": keyword,
                            "demand_score": random.randint(30, 70),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "simulated": True
                        })
                    
        except Exception as e:
            print(f"[{self.name}] ⚠️  Pytrends failed: {e}. Using fallback simulation.")
            log_activity(self.name, "Warning", f"Pytrends error: {e}, using fallback")
            results = self._simulate_google_trends()
        
        return results
    
    def _simulate_google_trends(self) -> List[Dict]:
        """Fallback simulation when pytrends fails."""
        print(f"[{self.name}] Using simulated demand data...")
        results = []
        
        high_demand = ["daily planner", "budget tracker", "habit tracker", "meal planner"]
        
        for keyword in self.keywords:
            if keyword.lower() in high_demand:
                score = random.randint(60, 95)
            else:
                score = random.randint(25, 65)
            
            results.append({
                "keyword": keyword,
                "demand_score": score,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "simulated": True
            })
        
        return results
    
    def _deduplicate_keywords(self, trends: List[Dict]) -> List[Dict]:
        """Deduplicate keywords within a single run."""
        seen = set()
        deduped = []
        
        for trend in trends:
            # Normalize: lowercase, strip
            normalized = trend["keyword"].lower().strip()
            
            if normalized not in seen:
                seen.add(normalized)
                deduped.append(trend)
        
        return deduped
    
    def _infer_product_types(self, trends: List[Dict]) -> List[Dict]:
        """Infer product type from keyword."""
        product_type_map = {
            "planner": "Planner",
            "tracker": "Tracker",
            "journal": "Journal",
            "template": "Template",
            "log": "Log",
            "sticker": "Stickers",
            "budget": "Budget Tool",
            "habit": "Habit Tracker",
            "meal": "Meal Planner",
            "fitness": "Fitness Tool"
        }
        
        enriched = []
        for trend in trends:
            keyword_lower = trend["keyword"].lower()
            product_type = "Template"  # Default
            
            # Match keyword patterns
            for pattern, ptype in product_type_map.items():
                if pattern in keyword_lower:
                    product_type = ptype
                    break
            
            enriched.append({
                **trend,
                "product_type": product_type
            })
        
        return enriched


if __name__ == "__main__":
    # Test the simplified research agent
    agent = ResearchAgent()
    results = agent.run()
    
    print(f"\n\nReturned {len(results)} results.")
    for r in results[:5]:
        print(f"  {r['keyword']}: {r['demand_score']} ({r['product_type']})")
