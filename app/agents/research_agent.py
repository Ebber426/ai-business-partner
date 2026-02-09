# Enhanced Research Agent
# Multi-source trend detection for digital products

import time
import random
from datetime import datetime, timezone
from typing import List, Dict, Optional

from pytrends.request import TrendReq
from app.utils.google_sheets import save_research, log_activity
from app.integrations.reddit_scraper import RedditResearcher
from app.integrations.simulated_trends import SimulatedTrendSource


class ResearchAgent:
    """
    Multi-source Research Agent for digital product trend detection.
    
    Data Sources:
    - Google Trends (pytrends) - search growth signals
    - Reddit (PRAW) - discussion volume signals  
    - Etsy (simulated) - buyer intent signals
    - Pinterest (simulated) - search growth signals
    
    Output Schema:
    {
        keyword: string,
        source: "google_trends" | "reddit" | "simulated_etsy" | "simulated_pinterest",
        signal_type: "search_growth" | "discussion_volume" | "buyer_intent",
        score: number,
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
        "bullet journal template"
    ]
    
    # Scoring weights
    WEIGHTS = {
        "search_growth": 0.5,      # Google Trends weight
        "discussion_volume": 0.3,  # Reddit weight
        "buyer_intent": 0.2        # Simulated Etsy weight
    }
    
    def __init__(self, keywords: Optional[List[str]] = None):
        self.name = "Research Agent"
        self.keywords = keywords or self.DEFAULT_KEYWORDS
        
        # Initialize data sources
        self.reddit = RedditResearcher()
        self.simulated = SimulatedTrendSource()

    def run(self, log_to_sheets: bool = True) -> List[Dict]:
        """
        Execute the full research pipeline.
        
        Returns:
            List of normalized trend data, sorted by composite score
        """
        log_activity(self.name, "Start", f"Researching {len(self.keywords)} keywords")
        print(f"\n🔍 Starting research for {len(self.keywords)} keywords...\n")
        
        all_results = []
        
        # 1. Google Trends
        print("📈 Fetching Google Trends...")
        google_results = self._get_google_trends()
        all_results.extend(google_results)
        print(f"   Found {len(google_results)} Google Trends signals")
        
        # 2. Reddit
        print("💬 Searching Reddit discussions...")
        reddit_results = self.reddit.search_trends(self.keywords)
        all_results.extend(reddit_results)
        print(f"   Found {len(reddit_results)} Reddit signals")
        
        # 3. Simulated Etsy & Pinterest
        print("🛒 Generating Etsy/Pinterest simulations...")
        simulated_results = self.simulated.get_combined_simulation(self.keywords)
        all_results.extend(simulated_results)
        print(f"   Generated {len(simulated_results)} simulated signals")
        
        if not all_results:
            log_activity(self.name, "Warning", "No trends found")
            return []
        
        # 4. Calculate composite scores per keyword
        print("\n📊 Calculating composite scores...")
        ranked_products = self._calculate_composite_scores(all_results)
        
        # 5. Get top 5 product ideas
        top_5 = ranked_products[:5]
        
        # 6. Log to console
        print("\n" + "="*60)
        print("🏆 TOP 5 PRODUCT IDEAS")
        print("="*60)
        for i, product in enumerate(top_5, 1):
            print(f"\n{i}. {product['keyword'].title()}")
            print(f"   Composite Score: {product['composite_score']:.1f}")
            print(f"   Search Growth:   {product.get('search_growth_score', 0):.1f}")
            print(f"   Discussion:      {product.get('discussion_score', 0):.1f}")
            print(f"   Buyer Intent:    {product.get('buyer_intent_score', 0):.1f}")
        print("\n" + "="*60)
        
        # 7. Log to Google Sheets
        if log_to_sheets:
            self._log_results_to_sheets(ranked_products)
        
        log_activity(self.name, "Success", f"Found {len(ranked_products)} trends, top: {top_5[0]['keyword'] if top_5 else 'none'}")
        
        # Return normalized format for orchestrator
        return self._normalize_for_output(ranked_products)
    
    def _get_google_trends(self) -> List[Dict]:
        """Fetch trend data from Google Trends using pytrends."""
        results = []
        
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Process in batches of 5 (pytrends limit)
            for i in range(0, len(self.keywords), 5):
                batch = self.keywords[i:i+5]
                
                try:
                    pytrends.build_payload(
                        batch, 
                        cat=0, 
                        timeframe='today 1-m', 
                        geo='', 
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
                                    "source": "google_trends",
                                    "signal_type": "search_growth",
                                    "score": round(score, 2),
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "notes": "30-day average interest"
                                })
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    print(f"   Batch error: {e}")
                    continue
                    
        except Exception as e:
            print(f"   Pytrends failed: {e}. Using simulated data.")
            log_activity(self.name, "Warning", f"Pytrends error: {e}")
            results = self._simulate_google_trends()
        
        return results
    
    def _simulate_google_trends(self) -> List[Dict]:
        """Fallback simulated Google Trends data."""
        results = []
        
        high_volume = ["daily planner", "budget tracker", "habit tracker"]
        
        for keyword in self.keywords:
            if keyword.lower() in high_volume:
                score = random.randint(60, 95)
            else:
                score = random.randint(25, 65)
            
            results.append({
                "keyword": keyword,
                "source": "google_trends",
                "signal_type": "search_growth",
                "score": score,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "notes": "Simulated (pytrends fallback)",
                "simulated": True
            })
        
        return results
    
    def _calculate_composite_scores(self, all_results: List[Dict]) -> List[Dict]:
        """
        Calculate composite scores for each keyword.
        
        Formula: score = (search_growth * 0.5) + (discussion_volume * 0.3) + (buyer_intent * 0.2)
        """
        # Group by keyword
        keyword_data = {}
        
        for result in all_results:
            kw = result["keyword"].lower()
            if kw not in keyword_data:
                keyword_data[kw] = {
                    "keyword": result["keyword"],
                    "search_growth_scores": [],
                    "discussion_scores": [],
                    "buyer_intent_scores": [],
                    "sources": []
                }
            
            signal_type = result.get("signal_type", "")
            score = result.get("score", 0)
            
            if signal_type == "search_growth":
                keyword_data[kw]["search_growth_scores"].append(score)
            elif signal_type == "discussion_volume":
                keyword_data[kw]["discussion_scores"].append(score)
            elif signal_type == "buyer_intent":
                keyword_data[kw]["buyer_intent_scores"].append(score)
            
            keyword_data[kw]["sources"].append(result["source"])
        
        # Calculate composite scores
        ranked = []
        
        for kw, data in keyword_data.items():
            # Average each signal type
            search_growth = sum(data["search_growth_scores"]) / len(data["search_growth_scores"]) if data["search_growth_scores"] else 0
            discussion = sum(data["discussion_scores"]) / len(data["discussion_scores"]) if data["discussion_scores"] else 0
            buyer_intent = sum(data["buyer_intent_scores"]) / len(data["buyer_intent_scores"]) if data["buyer_intent_scores"] else 0
            
            # Apply weights
            composite = (
                search_growth * self.WEIGHTS["search_growth"] +
                discussion * self.WEIGHTS["discussion_volume"] +
                buyer_intent * self.WEIGHTS["buyer_intent"]
            )
            
            ranked.append({
                "keyword": data["keyword"],
                "composite_score": round(composite, 2),
                "search_growth_score": round(search_growth, 2),
                "discussion_score": round(discussion, 2),
                "buyer_intent_score": round(buyer_intent, 2),
                "sources": list(set(data["sources"])),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Sort by composite score descending
        ranked.sort(key=lambda x: x["composite_score"], reverse=True)
        
        return ranked
    
    def _log_results_to_sheets(self, results: List[Dict]):
        """Log research results to Google Sheets."""
        try:
            for result in results[:10]:  # Log top 10
                save_research({
                    "keyword": result["keyword"],
                    "platform": ", ".join(result["sources"]),
                    "signal": result["composite_score"],
                    "notes": f"SG:{result['search_growth_score']} DV:{result['discussion_score']} BI:{result['buyer_intent_score']}"
                })
            print(f"\n📝 Logged {min(10, len(results))} results to Google Sheets")
        except Exception as e:
            print(f"⚠️  Failed to log to sheets: {e}")
    
    def _normalize_for_output(self, ranked: List[Dict]) -> List[Dict]:
        """Normalize output for orchestrator compatibility."""
        return [
            {
                "keyword": r["keyword"],
                "platform": "Multi-Source",
                "signal": r["composite_score"],
                "notes": f"Top signals from: {', '.join(r['sources'])}"
            }
            for r in ranked
        ]


if __name__ == "__main__":
    # Test the enhanced research agent
    agent = ResearchAgent()
    results = agent.run(log_to_sheets=False)
    
    print(f"\n\nReturned {len(results)} results for orchestrator.")
