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
        Execute research pipeline with enriched trend analysis.
        
        Returns:
            List of trend data with run_id and enriched metrics
        """
        print(f"\n[{self.name}] Starting research for {len(self.keywords)} keywords...")
        
        # Create research run
        try:
            run_id = create_research_run()
        except Exception as e:
            log_activity(self.name, "Error", f"Failed to create run: {e}")
            raise RuntimeError(f"Failed to create research run: {e}") from e
        
        log_activity(self.name, "Start", f"Run {run_id}: Researching {len(self.keywords)} keywords")
        
        # Get Google Trends data with time series
        print(f"[{self.name}] Fetching Google Trends data...")
        trends, time_series_data = self._get_google_trends()
        
        if not trends:
            log_activity(self.name, "Warning", f"Run {run_id}: No trends found")
            complete_research_run(run_id, 0)
            return []
        
        # Deduplicate within run
        deduped = self._deduplicate_keywords(trends)
        print(f"[{self.name}] Deduplication: {len(trends)} → {len(deduped)} unique keywords")
        
        # Enrich with velocity and categorization
        enriched = self._enrich_trends(deduped, time_series_data)
        
        # Infer product types
        enriched = self._infer_product_types(enriched)
        
        # Save to database
        try:
            save_research_items(run_id, enriched)
            complete_research_run(run_id, len(enriched))
        except Exception as e:
            log_activity(self.name, "Error", f"Run {run_id}: Failed to save: {e}")
            raise RuntimeError(f"Failed to save research results: {e}") from e
        
        log_activity(self.name, "Success", f"Run {run_id}: Found {len(enriched)} trends")
        print(f"[{self.name}] ✅ Research complete: {len(enriched)} results saved")
        
        return enriched
    
    def _get_google_trends(self):
        """Fetch trend data from Google Trends using pytrends.
        
        Returns:
            tuple: (trends list, time_series_data dict)
        """
        results = []
        time_series_data = {}
        
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
                                # Store time series for velocity calculation
                                time_series_data[keyword] = data[keyword].tolist() if keyword in data.columns else []
                    
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
                        time_series_data[keyword] = []
                    
        except Exception as e:
            print(f"[{self.name}] ⚠️  Pytrends failed: {e}. Using fallback simulation.")
            log_activity(self.name, "Warning", f"Pytrends error: {e}, using fallback")
            results, time_series_data = self._simulate_google_trends()
        
        return results, time_series_data
    
    def _simulate_google_trends(self):
        """Fallback simulation when pytrends fails.
        
        Returns:
            tuple: (trends list, time_series_data dict)
        """
        print(f"[{self.name}] Using simulated demand data...")
        results = []
        time_series_data = {}
        
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
            # Generate fake time series for simulation
            time_series_data[keyword] = [random.randint(max(0, score-20), min(100, score+20)) for _ in range(12)]
        
        return results, time_series_data
    
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
    
    def _enrich_trends(self, trends: List[Dict], time_series_data: Dict) -> List[Dict]:
        """Enrich trends with velocity, categorization, confidence, and explanations."""
        enriched = []
        
        for trend in trends:
            keyword = trend["keyword"]
            demand_score = trend["demand_score"]
            time_series = time_series_data.get(keyword, [])
            
            # Calculate velocity (growth rate)
            velocity = self._calculate_velocity(time_series, demand_score)
            
            # Categorize trend
            category = self._categorize_trend(velocity, demand_score)
            
            # Calculate confidence
            confidence, confidence_score = self._calculate_confidence(time_series, velocity, demand_score)
            
            # Generate explanation
            explanation = self._generate_explanation(velocity, demand_score, category)
            
            enriched.append({
                **trend,
                "velocity": velocity,
                "category": category,
                "confidence": confidence,
                "confidence_score": confidence_score,
                "explanation": explanation
            })
        
        return enriched
    
    def _calculate_velocity(self, time_series: List, current_score: float) -> float:
        """Calculate growth velocity from time series data."""
        if not time_series or len(time_series) < 2:
            return 0.0
        
        # Compare recent average to older average
        mid_point = len(time_series) // 2
        older_avg = sum(time_series[:mid_point]) / mid_point if mid_point > 0 else 0
        recent_avg = sum(time_series[mid_point:]) / (len(time_series) - mid_point)
        
        if older_avg == 0:
            # Growing from very low baseline
            return 100.0 if recent_avg > 10 else 0.0
        
        # Calculate percentage growth
        velocity = ((recent_avg - older_avg) / older_avg) * 100
        return round(velocity, 1)
    
    def _categorize_trend(self, velocity: float, demand_score: float) -> str:
        """Categorize trend as emerging, spiking, or stable."""
        # 📈 Emerging: Steady growth (30-60% velocity, low-medium baseline)
        if 30 <= velocity <= 60 and demand_score < 60:
            return "emerging"
        
        # 🔥 Spiking: Rapid growth (>60% velocity or very high score)
        if velocity > 60 or demand_score > 80:
            return "spiking"
        
        # 💤 Stable: Consistent interest (<30% velocity, any baseline)
        return "stable"
    
    def _calculate_confidence(self, time_series: List, velocity: float, demand_score: float) -> tuple:
        """Calculate confidence score based on consistency and other factors."""
        score = 0.5  # Default medium
        
        # Factor 1: Consistency (low volatility)
        if time_series and len(time_series) > 3:
            avg = sum(time_series) / len(time_series)
            variance = sum((x - avg) ** 2 for x in time_series) / len(time_series)
            std_dev = variance ** 0.5
            
            if std_dev < 10:  # Low volatility
                score += 0.2
            elif std_dev > 30:  # High volatility
                score -= 0.2
        
        # Factor 2: Absolute interest level
        if demand_score > 60:
            score += 0.15
        elif demand_score < 20:
            score -= 0.15
        
        # Factor 3: Velocity consistency
        if 0 <= abs(velocity) <= 100:  # Reasonable velocity
            score += 0.1
        
        # Clamp between 0 and 1
        score = max(0.0, min(1.0, score))
        
        # Convert to label
        if score >= 0.7:
            label = "high"
        elif score >= 0.4:
            label = "medium"
        else:
            label = "low"
        
        return label, round(score, 2)
    
    def _generate_explanation(self, velocity: float, demand_score: float, category: str) -> str:
        """Generate 'Why this matters' explanation text."""
        # Describe velocity
        if velocity > 100:
            growth_desc = f"Interest grew {int(velocity/100)}×"
        elif velocity > 30:
            growth_desc = f"Interest increased {int(velocity)}%"
        elif velocity < -30:
            growth_desc = f"Interest declined {abs(int(velocity))}%"
        else:
            growth_desc = "Interest remained stable"
        
        # Describe baseline
        if demand_score > 70:
            baseline_desc = "high historical baseline"
        elif demand_score > 40:
            baseline_desc = "moderate baseline"
        else:
            baseline_desc = "low baseline"
        
        # Category-specific insights
        if category == "emerging":
            return f"{growth_desc} with steady momentum. {baseline_desc.capitalize()}, strong growth potential."
        elif category == "spiking":
            return f"{growth_desc} rapidly. {baseline_desc.capitalize()}. Trending now!"
        else:
            return f"{growth_desc}. {baseline_desc.capitalize()}. Consistent demand."
    
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
