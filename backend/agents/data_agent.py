from azure_openai_client import azure_client
from chromadb_client import chromadb
from typing import Dict, Any, List
import logging
import json

logger = logging.getLogger(__name__)

class DataAgent:
    """Agentic AI workflow for intelligent data querying and insights with RAG"""
    
    def __init__(self):
        self.system_message = """You are an intelligent data analyst AI assistant for a retail chain store management system.
        You have access to various data sources including:
        - Store performance metrics (sales, revenue, foot traffic)
        - Sentiment analysis scorecards from customer reviews
        - Visual analysis scorecards from store images/videos
        - Alerts and incidents
        - Employee shift data
        - Inventory and stocking information
        - Transaction data
        - Image and video analysis insights

        Your role is to:
        1. Interpret natural language queries from store managers
        2. Analyze data to provide actionable insights
        3. Compare store performances
        4. Identify trends and patterns
        5. Provide recommendations for improvement
        6. Explain correlations between different metrics

        Always provide clear, concise, and actionable responses based on the provided data."""
    
    async def query(self, user_query: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process natural language query with context data using RAG pattern"""
        
        if not azure_client.is_configured():
            return {
                "response": "Azure OpenAI is not configured. Please configure to use the data agent.",
                "insights": [],
                "recommendations": []
            }
        
        try:
            # Step 1: Query ChromaDB for relevant documents using RAG
            retrieved_context = await self._retrieve_relevant_context(user_query)
            
            # Step 2: Combine retrieved context with provided context
            combined_context = {
                "provided_data": context_data,
                "retrieved_from_database": retrieved_context
            }
            
            context_str = json.dumps(combined_context, indent=2, default=str)
            
            # Step 3: Send to Azure OpenAI with full context
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": f"""Based on the following data context:

            {context_str}

            User Query: {user_query}

            Provide a detailed analysis and answer. Structure your response as JSON:
            {{
                "response": "Main answer to the query",
                "insights": ["Key insight 1", "Key insight 2", ...],
                "recommendations": ["Recommendation 1", "Recommendation 2", ...],
                "metrics_referenced": ["metric1", "metric2", ...]
            }}"""}
                        ]
            
            response_text = await azure_client.chat_completion(messages, temperature=0.5, max_tokens=2000)
            
            try:
                result = json.loads(response_text)
                return result
            except:
                # If JSON parsing fails, return structured response
                return {
                    "response": response_text,
                    "insights": [],
                    "recommendations": []
                }
        
        except Exception as e:
            logger.error(f"Error in data agent query: {str(e)}")
            return {
                "response": f"Error processing query: {str(e)}",
                "insights": [],
                "recommendations": []
            }
    
    async def _retrieve_relevant_context(self, query: str, n_results: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve relevant documents from ChromaDB collections using semantic search"""
        try:
            # Generate embedding for the query
            query_embedding = chromadb._create_embeddings([query])[0]
            
            retrieved_data = {}
            
            # Query each collection
            collections = {
                "reviews": chromadb.reviews,
                "sentiment_scorecards": chromadb.sentiment_scorecards,
                "visual_scorecards": chromadb.visual_scorecards,
                "alerts": chromadb.alerts,
                "reports": chromadb.reports,
                "stores": chromadb.stores
            }
            
            # Also query specialized collections if they exist
            try:
                transactions = chromadb.client.get_collection("transactions")
                collections["transactions"] = transactions
            except:
                pass
            
            try:
                employee_shifts = chromadb.client.get_collection("employee_shifts")
                collections["employee_shifts"] = employee_shifts
            except:
                pass
            
            try:
                employee_info = chromadb.client.get_collection("employee_info")
                collections["employee_info"] = employee_info
            except:
                pass
            
            try:
                image_insights = chromadb.client.get_collection("image_insights")
                collections["image_insights"] = image_insights
            except:
                pass
            
            try:
                video_insights = chromadb.client.get_collection("video_insights")
                collections["video_insights"] = video_insights
            except:
                pass
            
            try:
                documents = chromadb.client.get_collection("documents")
                collections["documents"] = documents
            except:
                pass
            
            # Query each collection
            for collection_name, collection in collections.items():
                try:
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(n_results, collection.count()) if collection.count() > 0 else 0
                    )
                    
                    if results and results["documents"] and results["documents"][0]:
                        retrieved_data[collection_name] = []
                        for i, doc in enumerate(results["documents"][0]):
                            retrieved_data[collection_name].append({
                                "document": doc,
                                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                                "distance": results["distances"][0][i] if "distances" in results else None
                            })
                except Exception as e:
                    logger.warning(f"Error querying collection {collection_name}: {str(e)}")
                    continue
            
            return retrieved_data
            
        except Exception as e:
            logger.error(f"Error retrieving context from ChromaDB: {str(e)}")
            return {}
    
    async def generate_insights(self, store_data: Dict[str, Any]) -> List[str]:
        """Generate proactive insights from store data"""
        
        if not azure_client.is_configured():
            return ["Azure OpenAI not configured"]
        
        try:
            prompt = f"""Analyze the following store performance data and generate 3-5 key insights:

            {json.dumps(store_data, indent=2, default=str)}

            Provide insights that are:
            1. Actionable and specific
            2. Data-driven
            3. Relevant to store operations
            4. Easy to understand

            Return as JSON array of strings: ["insight1", "insight2", ...]"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await azure_client.chat_completion(messages, temperature=0.6)
            
            try:
                insights = json.loads(response)
                return insights if isinstance(insights, list) else [response]
            except:
                return [response]
        
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    async def compare_stores(self, store1_data: Dict[str, Any], store2_data: Dict[str, Any]) -> str:
        """Compare two stores and provide analysis"""
        
        if not azure_client.is_configured():
            return "Azure OpenAI not configured"
        
        try:
            prompt = f"""Compare these two stores and provide a detailed analysis:

            Store 1:
            {json.dumps(store1_data, indent=2, default=str)}

            Store 2:
            {json.dumps(store2_data, indent=2, default=str)}

            Provide:
            1. Key differences in performance
            2. Which store is performing better and why
            3. What the lower-performing store can learn from the better one
            4. Specific actionable recommendations"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await azure_client.chat_completion(messages, temperature=0.5, max_tokens=2000)
            return response
        
        except Exception as e:
            logger.error(f"Error comparing stores: {str(e)}")
            return f"Error: {str(e)}"

data_agent = DataAgent()
