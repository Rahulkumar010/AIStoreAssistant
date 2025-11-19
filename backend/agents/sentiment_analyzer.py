from azure_openai_client import azure_client
from models import SentimentScorecard, SentimentTheme, Review
from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.default_themes = [
            "waiting_time",
            "staff_behavior",
            "cleanliness",
            "ease_of_locating_items",
            "product_availability",
            "store_layout"
        ]
        
        self.default_weightages = {
            "waiting_time": 0.20,
            "staff_behavior": 0.25,
            "cleanliness": 0.15,
            "ease_of_locating_items": 0.15,
            "product_availability": 0.15,
            "store_layout": 0.10
        }
    
    async def analyze_reviews(self, store_id: str, store_name: str, reviews: List[Review], 
                             custom_weightages: Dict[str, float] = None) -> SentimentScorecard:
        """Analyze reviews and generate sentiment scorecard"""
        
        if not azure_client.is_configured():
            logger.warning("Azure OpenAI not configured, returning mock data")
            return self._generate_mock_scorecard(store_id, store_name, len(reviews))
        
        weightages = custom_weightages or self.default_weightages
        review_texts = [review.review_text for review in reviews]
        
        try:
            # Call Azure OpenAI for sentiment analysis
            result = await azure_client.analyze_sentiment(review_texts, self.default_themes)
            
            themes = []
            for theme_data in result.get('themes', []):
                theme = SentimentTheme(
                    theme=theme_data['theme'],
                    score=theme_data['score'],
                    weightage=weightages.get(theme_data['theme'], 0.1),
                    sample_reviews=theme_data.get('sample_quotes', [])[:3]
                )
                themes.append(theme)
            
            # Calculate overall weighted score
            overall_score = sum(theme.score * theme.weightage for theme in themes)
            
            scorecard = SentimentScorecard(
                store_id=store_id,
                store_name=store_name,
                overall_score=overall_score,
                themes=themes,
                total_reviews_analyzed=len(reviews)
            )
            
            return scorecard
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return self._generate_mock_scorecard(store_id, store_name, len(reviews))
    
    def _generate_mock_scorecard(self, store_id: str, store_name: str, review_count: int) -> SentimentScorecard:
        """Generate mock scorecard for testing"""
        themes = [
            SentimentTheme(
                theme="waiting_time",
                score=0.6,
                weightage=0.20,
                sample_reviews=["Quick checkout", "Minimal wait time"]
            ),
            SentimentTheme(
                theme="staff_behavior",
                score=0.8,
                weightage=0.25,
                sample_reviews=["Very helpful staff", "Friendly service"]
            ),
            SentimentTheme(
                theme="cleanliness",
                score=0.7,
                weightage=0.15,
                sample_reviews=["Clean and tidy", "Well maintained"]
            )
        ]
        
        overall_score = sum(theme.score * theme.weightage for theme in themes)
        
        return SentimentScorecard(
            store_id=store_id,
            store_name=store_name,
            overall_score=overall_score,
            themes=themes,
            total_reviews_analyzed=review_count
        )

sentiment_analyzer = SentimentAnalyzer()
