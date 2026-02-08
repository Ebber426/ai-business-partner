
import time
import random
from pytrends.request import TrendReq
from app.utils.google_sheets import save_research, log_activity

class ResearchAgent:
    def __init__(self):
        self.name = "Research Agent"
        self.keywords = [
            "daily planner", 
            "budget tracker", 
            "habit tracker", 
            "study planner", 
            "fitness journal", 
            "digital stickers"
        ]

    def run(self):
        """Executes the research process."""
        log_activity(self.name, "Start", "Initiating trend research")
        
        try:
            # Attempt to use pytrends
            trends = self.get_google_trends()
        except Exception as e:
            print(f"Pytrends failed: {e}. Falling back to simulated data for MVP.")
            log_activity(self.name, "Error", f"Pytrends error: {e}")
            trends = self.get_simulated_trends()

        if trends:
            save_research(trends)
            log_activity(self.name, "Success", f"Found {len(trends)} trends")
            return trends
        else:
            log_activity(self.name, "Warning", "No trends found")
            return []

    def get_google_trends(self):
        """Fetches trend data from Google Trends."""
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # Pytrends can be flaky without proxies, so we handle it gracefully
        # We'll check interest over the last 30 days
        pytrends.build_payload(self.keywords, cat=0, timeframe='today 1-m', geo='', gprop='')
        
        data = pytrends.interest_over_time()
        
        results = []
        if not data.empty:
            means = data.mean()
            for keyword in self.keywords:
                score = means.get(keyword, 0)
                if score > 0: # Filter out zero interest
                    results.append({
                        "keyword": keyword,
                        "platform": "Google Trends",
                        "signal": round(score, 2),
                        "notes": "Interest over last 30 days"
                    })
        
        # Sort by signal strength
        results.sort(key=lambda x: x['signal'], reverse=True)
        return results

    def get_simulated_trends(self):
        """Returns simulated trend data for MVP demonstration."""
        # In a real MVP, if scraping fails, we don't want to stop.
        results = []
        for kw in self.keywords:
            score = random.randint(20, 100)
            results.append({
                        "keyword": kw,
                        "platform": "Simulated",
                        "signal": score,
                        "notes": "Simulated data (fallback)"
                    })
        results.sort(key=lambda x: x['signal'], reverse=True)
        return results

if __name__ == "__main__":
    agent = ResearchAgent()
    print(agent.run())
