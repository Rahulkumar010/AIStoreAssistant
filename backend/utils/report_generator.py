from azure_openai_client import azure_client
from models import ExecutiveReport
from typing import Dict, Any, List
import logging
import json

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate executive reports combining all data sources"""
    
    async def generate_executive_report(self, store_id: str, store_name: str,
                                       sales_data: Dict[str, Any],
                                       sentiment_data: Dict[str, Any],
                                       visual_data: Dict[str, Any],
                                       alerts: List[Dict[str, Any]]) -> ExecutiveReport:
        """Generate comprehensive executive one-pager report"""
        
        if not azure_client.is_configured():
            return self._generate_mock_report(store_id, store_name, sales_data)
        
        try:
            # Prepare data summary
            data_summary = {
                "sales": sales_data,
                "sentiment": sentiment_data,
                "visual": visual_data,
                "alerts": alerts
            }
            
            prompt = f"""Generate an executive summary report for a retail store based on the following data:

            {json.dumps(data_summary, indent=2, default=str)}

            Provide:
            1. Key highlights (3-5 bullet points)
            2. Performance insights (3-5 insights)
            3. Actionable recommendations (3-5 recommendations)
            4. Critical issues that need immediate attention

            Keep it concise and executive-friendly. Focus on actionable insights.

            Respond in JSON format:
            {{
                "key_highlights": ["highlight1", "highlight2", ...],
                "insights": ["insight1", "insight2", ...],
                "recommendations": ["rec1", "rec2", ...],
                "critical_issues": ["issue1", "issue2", ...]
            }}"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await azure_client.chat_completion(messages, temperature=0.5, max_tokens=2000)
            
            try:
                report_data = json.loads(response)
            except:
                report_data = {
                    "key_highlights": ["Report generated"],
                    "insights": [response[:200]],
                    "recommendations": [],
                    "critical_issues": []
                }
            
            # Combine insights and recommendations
            all_insights = report_data.get('key_highlights', []) + report_data.get('insights', [])
            
            report = ExecutiveReport(
                store_id=store_id,
                store_name=store_name,
                period="Current Period",
                sales_summary=sales_data,
                sentiment_summary=sentiment_data,
                visual_summary=visual_data,
                key_insights=all_insights,
                recommendations=report_data.get('recommendations', [])
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return self._generate_mock_report(store_id, store_name, sales_data)
    
    def _generate_mock_report(self, store_id: str, store_name: str, 
                             sales_data: Dict[str, Any]) -> ExecutiveReport:
        """Generate mock report for testing"""
        return ExecutiveReport(
            store_id=store_id,
            store_name=store_name,
            period="Current Period",
            sales_summary=sales_data or {},
            sentiment_summary={"overall_score": 0.7},
            visual_summary={"overall_score": 75},
            key_insights=[
                "Store performance is stable",
                "Customer sentiment is generally positive",
                "Some operational areas need attention"
            ],
            recommendations=[
                "Focus on reducing queue times",
                "Improve shelf stocking processes",
                "Enhance staff training"
            ]
        )

report_generator = ReportGenerator()
