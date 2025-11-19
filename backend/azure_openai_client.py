from openai import AzureOpenAI
from config import config
import base64
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AzureOpenAIClient:
    def __init__(self):
        # For mock mode with mock credentials, don't initialize real client
        if not config.is_azure_configured() or config.AZURE_OPENAI_API_KEY.startswith("mock"):
            logger.warning("Azure OpenAI is in mock mode or not configured.")
            self.client = None
        else:
            try:
                self.client = AzureOpenAI(
                    api_key=config.AZURE_OPENAI_API_KEY,
                    api_version=config.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=config.AZURE_OPENAI_ENDPOINT
                )
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
                self.client = None
    
    def is_configured(self) -> bool:
        return self.client is not None
    
    async def chat_completion(self, messages: List[Dict[str, Any]], deployment: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1500) -> str:
        """General chat completion for text generation"""
        if not self.is_configured():
            return "Azure OpenAI is not configured. Please set API credentials."
        
        try:
            deployment_name = deployment or config.AZURE_OPENAI_DEPLOYMENT
            response = self.client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {str(e)}")
            raise Exception(f"Failed to get completion: {str(e)}")
    
    async def analyze_image(self, image_path: str, prompt: str, deployment: Optional[str] = None) -> str:
        """Analyze image using GPT-4 Vision"""
        if not self.is_configured():
            return "Azure OpenAI is not configured. Please set API credentials."
        
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            deployment_name = deployment or config.AZURE_OPENAI_DEPLOYMENT
            
            response = self.client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                },
                                "detail": "low"
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            raise Exception(f"Failed to analyze image: {str(e)}")
    
    async def analyze_sentiment(self, reviews: List[str], themes: List[str]) -> Dict[str, Any]:
        """Analyze sentiment across multiple themes"""
        prompt = f"""Analyze the following customer reviews for a retail store and provide sentiment scores for each theme.

        Themes to analyze: {', '.join(themes)}

        Reviews:
        {chr(10).join([f'{i+1}. {review}' for i, review in enumerate(reviews)])}

        For each theme, provide:
        1. Sentiment score from -1 (very negative) to 1 (very positive)
        2. Brief explanation
        3. Sample quotes from reviews

        Respond in JSON format:
        {{
            "themes": [
                {{
                    "theme": "theme_name",
                    "score": 0.5,
                    "explanation": "brief explanation",
                    "sample_quotes": ["quote1", "quote2"]
                }}
            ],
            "overall_sentiment": 0.3
        }}"""
        
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, temperature=0.3)
        
        try:
            import json
            return json.loads(response.replace('```', '').replace('json',''))
        except Exception as e:
            logger.error(f"Azure: Sentiment analysis error: {str(e)}, response: {str(response)}")
            return {"themes": [], "overall_sentiment": 0}

# Global instance
azure_client = AzureOpenAIClient()
