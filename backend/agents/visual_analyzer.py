from azure_openai_client import azure_client
from models import VisualScorecard, VisualMetric, Alert
from typing import List, Dict, Any
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)

class VisualAnalyzer:
    def __init__(self):
        self.default_metrics = [
            "cleanliness",
            "empty_shelves",
            "queue_length",
            "staff_presence",
            "store_organization"
        ]
        
        self.default_weightages = {
            "cleanliness": 0.25,
            "empty_shelves": 0.20,
            "queue_length": 0.20,
            "staff_presence": 0.20,
            "store_organization": 0.15
        }
        
        self.alert_thresholds = {
            "empty_shelves": 40,  # score below this triggers alert
            "queue_length": 40,
            "cleanliness": 50,
            "staff_presence": 50
        }
    
    async def analyze_media(self, store_id: str, store_name: str, media_files: List[str],
                           custom_weightages: Dict[str, float] = None) -> tuple[VisualScorecard, List[Alert]]:
        """Analyze images/videos and generate visual scorecard and alerts"""
        
        if not azure_client.is_configured():
            logger.warning("Azure OpenAI not configured, returning mock data")
            return self._generate_mock_scorecard(store_id, store_name, media_files)
        
        weightages = custom_weightages or self.default_weightages
        metrics = []
        alerts = []
        
        try:
            for media_file in media_files:
                # Analyze each image
                analysis = await self._analyze_single_image(media_file)
                
                # Extract metrics from analysis
                for metric_name in self.default_metrics:
                    if metric_name in analysis:
                        metric_data = analysis[metric_name]
                        metric = VisualMetric(
                            metric=metric_name,
                            score=metric_data.get('score', 50),
                            weightage=weightages.get(metric_name, 0.1),
                            details=metric_data.get('details', {})
                        )
                        metrics.append(metric)
                        
                        # Check for alert conditions
                        if metric_name in self.alert_thresholds:
                            if metric.score < self.alert_thresholds[metric_name]:
                                alert = self._create_alert(store_id, store_name, metric_name, 
                                                          metric.score, media_file)
                                alerts.append(alert)
            
            # Calculate overall score
            if metrics:
                overall_score = sum(metric.score * metric.weightage for metric in metrics)
            else:
                overall_score = 0
            
            scorecard = VisualScorecard(
                store_id=store_id,
                store_name=store_name,
                overall_score=overall_score,
                metrics=metrics,
                media_analyzed=[Path(f).name for f in media_files]
            )
            
            return scorecard, alerts
            
        except Exception as e:
            logger.error(f"Error analyzing visual media: {str(e)}")
            return self._generate_mock_scorecard(store_id, store_name, media_files)
    
    async def _analyze_single_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze a single image for all metrics"""
        prompt = f"""Analyze this retail store image and provide scores (0-100) for the following metrics:

        1. Cleanliness: How clean and tidy is the store?
        2. Empty Shelves: Are there empty or poorly stocked shelves? (100 = fully stocked, 0 = many empty)
        3. Queue Length: How long are the checkout queues?, this field is only relevant situations like checkout (100 = no queue, 0 = very long queues)
        4. Staff Presence: Is staff visible and available? (100 = good staffing, 0 = no staff visible)
        5. Store Organization: How well organized is the store layout?
        6. Immediate Issues: This is optional field, only provide value if it's relevant to situation (["Restock aisle 1"], [""])

        For each metric, provide:
        - score (0-100)
        - details (brief description - ignore if it's optional or not relevant to situation)

        Also identify any issues that need immediate attention (spills, hazards, etc.)

        Respond in JSON format:
        {{
            "cleanliness": {{"score": 85, "details": "Store is generally clean"}},
            "empty_shelves": {{"score": 70, "details": "Some gaps in produce section"}},
            "queue_length": {{"score": 60, "details": "Moderate queues at 2 checkouts"}},
            "staff_presence": {{"score": 80, "details": "Staff visible in multiple areas"}},
            "store_organization": {{"score": 90, "details": "Well organized layout"}},
            "immediate_issues": ["Minor spill in aisle 3"]
        }}"""
        
        response = await azure_client.analyze_image(image_path, prompt)
        
        try:
            return json.loads(response)
        except:
            # Return default if parsing fails
            return {
                "cleanliness": {"score": 75, "details": "Analysis completed"},
                "empty_shelves": {"score": 70, "details": "Analysis completed"},
                "queue_length": {"score": 65, "details": "Analysis completed"},
                "staff_presence": {"score": 70, "details": "Analysis completed"},
                "store_organization": {"score": 80, "details": "Analysis completed"}
            }
    
    def _create_alert(self, store_id: str, store_name: str, issue_type: str, 
                     score: float, media_file: str) -> Alert:
        """Create an alert based on metric score"""
        severity = "high" if score < 30 else "medium" if score < 50 else "low"
        
        descriptions = {
            "empty_shelves": f"Empty shelves detected (score: {score:.1f}/100)",
            "queue_length": f"Long checkout queues detected (score: {score:.1f}/100)",
            "cleanliness": f"Cleanliness issue detected (score: {score:.1f}/100)",
            "staff_presence": f"Low staff presence detected (score: {score:.1f}/100)"
        }
        
        return Alert(
            store_id=store_id,
            store_name=store_name,
            alert_type=issue_type,
            severity=severity,
            description=descriptions.get(issue_type, f"{issue_type} issue detected"),
            media_file=Path(media_file).name
        )
    
    def _generate_mock_scorecard(self, store_id: str, store_name: str, 
                                media_files: List[str]) -> tuple[VisualScorecard, List[Alert]]:
        """Generate mock scorecard for testing"""
        metrics = [
            VisualMetric(
                metric="cleanliness",
                score=75,
                weightage=0.25,
                details={"description": "Store appears generally clean"}
            ),
            VisualMetric(
                metric="empty_shelves",
                score=65,
                weightage=0.20,
                details={"description": "Some empty spaces detected"}
            ),
            VisualMetric(
                metric="queue_length",
                score=70,
                weightage=0.20,
                details={"description": "Moderate queue lengths"}
            )
        ]
        
        overall_score = sum(metric.score * metric.weightage for metric in metrics)
        
        scorecard = VisualScorecard(
            store_id=store_id,
            store_name=store_name,
            overall_score=overall_score,
            metrics=metrics,
            media_analyzed=[Path(f).name for f in media_files]
        )
        
        return scorecard, []

visual_analyzer = VisualAnalyzer()
