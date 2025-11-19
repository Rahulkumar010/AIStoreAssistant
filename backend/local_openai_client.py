from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from config import config
import base64
import logging
from typing import List, Dict, Any, Optional, Union
import json

logger = logging.getLogger(__name__)


class LocalOpenAIClient:
    def __init__(self):
        # If mock/no credentials → disable client
        # if not config.is_local_configured() or config.Local_OPENAI_API_KEY.startswith("mock"):
        #     logger.warning("Local OpenAI is in mock mode or not configured.")
        #     self.llm = None
        # else:
        try:
            self.llm = ChatOpenAI(
                base_url="http://127.0.0.1:8080",
                model="",
                api_key="NA"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Local OpenAI client: {str(e)}")
            self.llm = None

    def is_configured(self) -> bool:
        return self.llm is not None

    # ----------------------------------------------------------------------
    # CHAT COMPLETION
    # ----------------------------------------------------------------------
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        deployment: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_model: Optional[Any] = None,
    ) -> Union[str, Dict]:

        if not self.is_configured():
            return "Local OpenAI is not configured. Please deploy the API endpoints."

        try:
            lc_messages = []
            # Convert dict messages → LangChain message objects
            for msg in messages:
                role = msg.get("role")
                content = msg.get("content")
                if role == "system":
                    lc_messages.append(SystemMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))
                else:
                    lc_messages.append(HumanMessage(content=content))

            llm = self.llm.bind(max_tokens=max_tokens, temperature=temperature)
            llm = self.llm.with_structured_output(response_model)

            response = await llm.ainvoke(lc_messages)
            return response.model_dump()

        except Exception as e:
            logger.error(f"Local OpenAI API error: {str(e)}")
            raise Exception(f"Failed to get completion: {str(e)}")

    # ----------------------------------------------------------------------
    # VISION / IMAGE ANALYSIS
    # ----------------------------------------------------------------------
    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        deployment: Optional[str] = None,
        response_model: Optional[Any] = None,
    ) -> Union[str, Dict]:

        if not self.is_configured():
            return "Local OpenAI is not configured. Please deploy API endpoints."

        try:
            # Encode image
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")

            msg = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded}"
                        }
                    }
                ]
            )

            llm = self.llm.with_structured_output(response_model)

            # response = await self.llm.ainvoke([msg, {"role": "system", "content": f"maintain the output format in {format_instructions}"}])
            response = await llm.ainvoke([msg])
            return response.model_dump()

        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            raise Exception(f"Failed to analyze image: {str(e)}")

    # ----------------------------------------------------------------------
    # SENTIMENT ANALYSIS (JSON OUTPUT)
    # ----------------------------------------------------------------------
    async def analyze_sentiment(self, reviews: List[str], 
                                themes: List[str],
                                response_model: Optional[Any] = None,
                                ) -> Union[str, Dict]:

        prompt = f"""
        Analyze the following customer reviews for a retail store and provide sentiment scores for each theme.

        Themes to analyze: {', '.join(themes)}

        Reviews:
        {chr(10).join([f"{i+1}. {review}" for i, review in enumerate(reviews)])}
        
        For each theme, provide:
        1. Sentiment score from -1 (very negative) to 1 (very positive)
        2. Brief explanation
        3. Sample quotes from reviews

        Respond in JSON with:
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
        }}
        """

        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, temperature=0.3, response_model=response_model)

        try:
            # cleaned = response.replace("```", "").replace("json", "")
            # return json.loads(cleaned)
            return response
        except Exception as e:
            logger.error(f"Local: Sentiment analysis error: {str(e)}, response: {response}")
            return {"themes": [], "overall_sentiment": 0}


# Global instance
local_client = LocalOpenAIClient()
