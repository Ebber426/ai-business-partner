# Reddit Integration using PRAW
# Official Reddit API - Free Tier

import os
import time
import random
from datetime import datetime, timezone
from typing import List, Dict, Optional

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    print("Warning: praw not installed. Run: pip install praw")


class RedditResearcher:
    """
    Searches Reddit for digital product trends using the official PRAW API.
    
    Focuses on subreddits where potential buyers discuss:
    - Productivity tools
    - Planners and templates
    - Side hustles and Etsy selling
    """
    
    # Target subreddits for digital product research
    SUBREDDITS = [
        "productivity",
        "sidehustle", 
        "Etsy",
        "EtsySellers",
        "bulletjournal",
        "planners",
        "studytips",
        "budgeting",
        "personalfinance",
        "ADHD",  # High demand for planners
    ]
    
    # Keywords indicating buyer intent
    BUYER_KEYWORDS = [
        "looking for", "need a", "recommend", "best", "where can i find",
        "template", "planner", "tracker", "printable", "spreadsheet",
        "budget", "habit", "goal", "schedule", "organizer"
    ]
    
    def __init__(self):
        """Initialize Reddit client using environment variables."""
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize PRAW client if credentials available."""
        if not PRAW_AVAILABLE:
            return
        
        # PRAW can work in read-only mode without user credentials
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        
        if client_id and client_secret:
            try:
                self.client = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent="AIBusinessPartner/1.0 (Digital Product Research)"
                )
                print("Reddit API connected (authenticated)")
            except Exception as e:
                print(f"Reddit auth failed: {e}")
        else:
            # Read-only mode (limited but works without credentials)
            try:
                self.client = praw.Reddit(
                    client_id="script",
                    client_secret=None,
                    user_agent="AIBusinessPartner/1.0 (Digital Product Research)"
                )
                print("Reddit API connected (read-only mode)")
            except Exception as e:
                print(f"Reddit connection failed: {e}")
    
    def search_trends(self, keywords: List[str], limit_per_sub: int = 10) -> List[Dict]:
        """
        Search Reddit for trending discussions about digital products.
        
        Args:
            keywords: List of product keywords to search
            limit_per_sub: Max posts to analyze per subreddit
            
        Returns:
            List of normalized trend data
        """
        if not self.client:
            print("Reddit client not available, using simulated data")
            return self._simulate_reddit_trends(keywords)
        
        results = []
        
        for keyword in keywords:
            keyword_results = self._search_keyword(keyword, limit_per_sub)
            results.extend(keyword_results)
            
            # Rate limiting - be respectful to Reddit API
            time.sleep(random.uniform(0.5, 1.5))
        
        return results
    
    def _search_keyword(self, keyword: str, limit: int) -> List[Dict]:
        """Search for a single keyword across target subreddits."""
        results = []
        
        for subreddit_name in self.SUBREDDITS[:5]:  # Limit subreddits for MVP
            try:
                subreddit = self.client.subreddit(subreddit_name)
                
                # Search recent posts
                posts = subreddit.search(
                    keyword, 
                    sort="relevance",
                    time_filter="month",
                    limit=limit
                )
                
                discussion_count = 0
                total_engagement = 0
                buyer_intent_signals = 0
                
                for post in posts:
                    discussion_count += 1
                    total_engagement += post.score + post.num_comments
                    
                    # Check for buyer intent
                    title_lower = post.title.lower()
                    if any(bk in title_lower for bk in self.BUYER_KEYWORDS):
                        buyer_intent_signals += 1
                
                if discussion_count > 0:
                    # Calculate scores
                    discussion_score = min(100, discussion_count * 10)
                    engagement_score = min(100, total_engagement / discussion_count)
                    buyer_intent_score = min(100, (buyer_intent_signals / discussion_count) * 100)
                    
                    results.append({
                        "keyword": keyword,
                        "source": "reddit",
                        "subreddit": subreddit_name,
                        "signal_type": "discussion_volume",
                        "score": round((discussion_score * 0.4 + engagement_score * 0.4 + buyer_intent_score * 0.2), 2),
                        "discussion_count": discussion_count,
                        "avg_engagement": round(total_engagement / discussion_count, 1),
                        "buyer_intent_signals": buyer_intent_signals,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
            except Exception as e:
                print(f"Error searching r/{subreddit_name} for '{keyword}': {e}")
                continue
            
            # Small delay between subreddit searches
            time.sleep(random.uniform(0.3, 0.8))
        
        return results
    
    def _simulate_reddit_trends(self, keywords: List[str]) -> List[Dict]:
        """Simulate Reddit trends when API is not available."""
        results = []
        
        # Simulated engagement patterns
        high_engagement_keywords = ["habit tracker", "budget tracker", "daily planner"]
        medium_engagement = ["study planner", "meal planner", "fitness journal"]
        
        for keyword in keywords:
            if keyword.lower() in high_engagement_keywords:
                base_score = random.randint(70, 95)
                discussion_count = random.randint(15, 30)
            elif keyword.lower() in medium_engagement:
                base_score = random.randint(50, 75)
                discussion_count = random.randint(8, 18)
            else:
                base_score = random.randint(25, 55)
                discussion_count = random.randint(3, 12)
            
            results.append({
                "keyword": keyword,
                "source": "reddit",
                "subreddit": "simulated",
                "signal_type": "discussion_volume",
                "score": base_score,
                "discussion_count": discussion_count,
                "avg_engagement": round(random.uniform(10, 50), 1),
                "buyer_intent_signals": random.randint(1, 5),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "simulated": True
            })
        
        return results


if __name__ == "__main__":
    # Test the Reddit researcher
    researcher = RedditResearcher()
    results = researcher.search_trends(["daily planner", "habit tracker"])
    
    for r in results:
        print(f"[{r['source']}] {r['keyword']}: score={r['score']}")
