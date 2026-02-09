# Simulated Trend Sources for Etsy & Pinterest
# MVP Implementation - Uses heuristics and keyword patterns
# No actual scraping - fully compliant with ToS

import random
from datetime import datetime, timezone
from typing import List, Dict


class SimulatedTrendSource:
    """
    Simulates trend data for Etsy and Pinterest.
    
    Uses keyword heuristics, seasonal patterns, and overlap with
    real data sources to estimate buyer intent.
    """
    
    # Seasonal modifiers (month -> keyword modifiers)
    SEASONAL_PATTERNS = {
        1: ["new year", "goal", "resolution", "planner", "budget"],
        2: ["valentine", "love", "february"],
        3: ["spring", "cleaning", "declutter"],
        4: ["easter", "spring", "tax"],
        5: ["mother", "graduation", "spring"],
        6: ["summer", "wedding", "father"],
        7: ["summer", "vacation", "travel"],
        8: ["back to school", "student", "college"],
        9: ["fall", "autumn", "organization"],
        10: ["halloween", "fall", "october"],
        11: ["thanksgiving", "gratitude", "holiday prep"],
        12: ["christmas", "holiday", "gift", "new year prep"]
    }
    
    # High-converting keywords on Etsy (based on market research)
    ETSY_HOT_KEYWORDS = {
        "daily planner": 90,
        "budget tracker": 88,
        "habit tracker": 85,
        "weekly planner": 82,
        "meal planner": 80,
        "fitness tracker": 78,
        "goal planner": 75,
        "study planner": 73,
        "digital stickers": 70,
        "bullet journal": 68,
    }
    
    # Pinterest trending categories
    PINTEREST_CATEGORIES = {
        "productivity": 85,
        "organization": 82,
        "minimalist": 78,
        "aesthetic": 75,
        "self care": 72,
        "wellness": 70,
    }
    
    def __init__(self):
        self.current_month = datetime.now().month
        self.seasonal_boost = self.SEASONAL_PATTERNS.get(self.current_month, [])
    
    def get_etsy_trends(self, keywords: List[str]) -> List[Dict]:
        """
        Simulate Etsy buyer intent signals.
        
        Scoring based on:
        - Keyword match to known high-converters
        - Seasonal relevance
        - Product type modifiers
        """
        results = []
        
        for keyword in keywords:
            kw_lower = keyword.lower()
            
            # Base score from known hot keywords
            base_score = 0
            for hot_kw, score in self.ETSY_HOT_KEYWORDS.items():
                if hot_kw in kw_lower or kw_lower in hot_kw:
                    base_score = max(base_score, score)
                    break
            
            if base_score == 0:
                base_score = random.randint(30, 60)
            
            # Seasonal boost
            seasonal_multiplier = 1.0
            for seasonal_kw in self.seasonal_boost:
                if seasonal_kw in kw_lower:
                    seasonal_multiplier = 1.2
                    break
            
            # Product type modifiers (templates sell well)
            type_modifier = 1.0
            if any(t in kw_lower for t in ["template", "printable", "spreadsheet"]):
                type_modifier = 1.15
            elif any(t in kw_lower for t in ["tracker", "planner", "journal"]):
                type_modifier = 1.1
            
            final_score = min(100, round(base_score * seasonal_multiplier * type_modifier))
            
            results.append({
                "keyword": keyword,
                "source": "simulated_etsy",
                "signal_type": "buyer_intent",
                "score": final_score,
                "seasonal_boost": seasonal_multiplier > 1.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "notes": "Simulated based on Etsy market patterns"
            })
        
        return results
    
    def get_pinterest_trends(self, keywords: List[str]) -> List[Dict]:
        """
        Simulate Pinterest trend signals.
        
        Scoring based on:
        - Category alignment
        - Aesthetic/visual keywords
        - Seasonal relevance
        """
        results = []
        
        for keyword in keywords:
            kw_lower = keyword.lower()
            
            # Base score from category match
            base_score = 0
            matched_category = None
            for category, score in self.PINTEREST_CATEGORIES.items():
                if category in kw_lower:
                    base_score = max(base_score, score)
                    matched_category = category
            
            if base_score == 0:
                base_score = random.randint(35, 65)
            
            # Aesthetic bonus (visual platforms favor these)
            aesthetic_bonus = 0
            aesthetic_terms = ["minimalist", "aesthetic", "cute", "boho", "modern", "pastel"]
            if any(term in kw_lower for term in aesthetic_terms):
                aesthetic_bonus = 15
            
            # Seasonal boost
            seasonal_multiplier = 1.0
            for seasonal_kw in self.seasonal_boost:
                if seasonal_kw in kw_lower:
                    seasonal_multiplier = 1.15
                    break
            
            final_score = min(100, round((base_score + aesthetic_bonus) * seasonal_multiplier))
            
            results.append({
                "keyword": keyword,
                "source": "simulated_pinterest",
                "signal_type": "search_growth",
                "score": final_score,
                "matched_category": matched_category,
                "seasonal_boost": seasonal_multiplier > 1.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "notes": "Simulated based on Pinterest category patterns"
            })
        
        return results
    
    def get_combined_simulation(self, keywords: List[str]) -> List[Dict]:
        """Get simulated trends from both Etsy and Pinterest."""
        etsy = self.get_etsy_trends(keywords)
        pinterest = self.get_pinterest_trends(keywords)
        return etsy + pinterest


if __name__ == "__main__":
    sim = SimulatedTrendSource()
    keywords = ["daily planner", "habit tracker", "minimalist budget template"]
    
    results = sim.get_combined_simulation(keywords)
    for r in results:
        print(f"[{r['source']}] {r['keyword']}: {r['score']}")
