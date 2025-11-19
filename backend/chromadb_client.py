import ast
import json
from chromadb import Client, PersistentClient
from chromadb.config import Settings
from config import config
from models import SentimentScorecard, VisualScorecard, Alert, Review, ExecutiveReport
from database_models import Store
from typing import List, Optional, Dict, Any
from utils.sql_handler import sql_handler
from azure_openai_client import azure_client
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        # Initialize Chroma client (persistent mode if configured)
        try:
            import os
            # Create directory if it doesn't exist, but DON'T delete existing data
            os.makedirs(config.CHROMA_DB_DIR, exist_ok=True)
            
            self.client = PersistentClient(path=config.CHROMA_DB_DIR)
            logger.info(f"Initialized ChromaDB at {config.CHROMA_DB_DIR}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise

        # Collections
        self.stores = self._get_or_create_collection("stores")
        self.sentiment_scorecards = self._get_or_create_collection("sentiment_scorecards")
        self.visual_scorecards = self._get_or_create_collection("visual_scorecards")
        self.alerts = self._get_or_create_collection("alerts")
        self.reviews = self._get_or_create_collection("reviews")
        self.reports = self._get_or_create_collection("reports")

    def _recursively_deserialize_lists(self, data):
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                if isinstance(v, str):
                    # Attempt to parse JSON string into Python object
                    try:
                        parsed = json.loads(v)
                        # Only replace if result is a list, set, tuple, or dict
                        if isinstance(parsed, (list, set, tuple)):
                            new_dict[k] = parsed
                        else:
                            new_dict[k] = parsed
                    except (json.JSONDecodeError, TypeError):
                        # Try parsing with ast.literal_eval for Python-style literals
                        try:
                            parsed = ast.literal_eval(v)
                            if isinstance(parsed, (list, set, tuple)):
                                new_dict[k] = parsed
                            else:
                                new_dict[k] = parsed
                        except (ValueError, SyntaxError):
                            # Not parseable — keep as-is
                            new_dict[k] = v
                elif isinstance(v, dict):
                    # Recursive call for nested dict
                    new_dict[k] = self._recursively_deserialize_lists(v)
                else:
                    new_dict[k] = v
            return new_dict
        else:
            return data
        
    def _recursively_serialize_lists(self, data):
        def _recursively_serialize(data):
            if isinstance(data, dict):
                new_dict = {}
                for k, v in data.items():
                    if isinstance(v, (list, set, tuple)):
                        # Serialize collection to JSON string
                        new_dict[k] = json.dumps(v)
                    elif isinstance(v, dict):
                        new_dict[k] = _recursively_serialize(v)
                    elif isinstance(v, datetime):
                        new_dict[k] = v.isoformat()
                    else:
                        new_dict[k] = v
                return new_dict
            else:
                # If not dict, return as-is
                return data
        def serialize(data):
            new_dict = {}
            for k, v in data.items():
                new_dict[k] = str(v)
            return new_dict

        return serialize(_recursively_serialize(data))

    def _create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Azure OpenAI or mock embeddings
        Args:
            texts (list[str]): A list of text documents to embed.
        Returns:
            list[list[float]]: List of generated embeddings.
        """
        # If Azure OpenAI is configured, use it
        if azure_client.is_configured():
            try:
                response = azure_client.client.embeddings.create(
                    model=config.AZURE_EMBEDDING_MODEL,
                    input=texts
                )
                embeddings = [item.embedding for item in response.data]
                return embeddings
            except Exception as e:
                logger.warning(f"Failed to create Azure embeddings, falling back to mock: {str(e)}")
        
        # Fallback to mock embeddings
        import random
        dimension = 1536  # Standard OpenAI embedding dimension
        return [[random.gauss(0, 0.1) for _ in range(dimension)] for _ in texts]

    def _get_or_create_collection(self, name: str):
        try:
            return self.client.get_collection(name)
        except Exception:
            return self.client.create_collection(name)

    async def close(self):
        # Chroma doesn’t maintain persistent connections, so nothing is required
        pass

    async def fetch_stores_from_sql(self, filters: Dict[str, Any] = {}) -> List[Store]:
        records = sql_handler.query_data('dbo.store_info', filters=filters)
        return [Store(**record) for record in records.to_dict(orient="records")]

    # Store operations
    async def create_store(self, store: Store) -> Store:
        data = store.model_dump()
        # Create text representation for document
        doc_text = f"Store {data['store_id']}: {data['full_address']}, Location: {data['geo_location_id']}"
        # Generate embeddings
        embeddings = self._create_embeddings([doc_text])
        self.stores.add(
            ids=[data["store_id"]], 
            metadatas=[data], 
            documents=[doc_text],
            embeddings=embeddings
        )
        return store

    async def get_store(self, store_id: str) -> Optional[Store]:
        results = self.stores.get(ids=[store_id])
        if results and results["metadatas"]:
            md = results["metadatas"][0]
            # Handle snake_case to aliased format conversion
            if "full_address" in md:
                store_data = {
                    "store_id": md.get("store_id"),
                    "full_address": md.get("full_address"),
                    "geo_location_id": md.get("geo_location_id"),
                    "store_images": md.get("store_images"),
                    "store_videos": md.get("store_videos")
                }
                return Store(**store_data)
            return Store(**md)
        else:
            # If Chroma has no stores, fetch from SQL
            logger.info("No stores found in Chroma, fetching from SQL database...")
            stores_from_sql = await self.fetch_stores_from_sql(filters={"Store ID": store_id})

            # Store fetched data in Chroma
            for store in stores_from_sql:
                data = store.model_dump()
                self.stores.add(ids=[data["store_id"]], metadatas=[data])
            
            results = self.stores.get(ids=[store_id])
            if results and results["metadatas"]:
                md = results["metadatas"][0]
                if "full_address" in md:
                    store_data = {
                        "store_id": md.get("store_id"),
                        "full_address": md.get("full_address"),
                        "geo_location_id": md.get("geo_location_id"),
                        "store_images": md.get("store_images"),
                        "store_videos": md.get("store_videos")
                    }
                    return Store(**store_data)
                return Store(**md)
            return None

    async def get_all_stores(self) -> List[Store]:
        results = self.stores.get()
        if results and results["metadatas"]:
            # Handle the stored data - convert back to aliased format for Pydantic
            stores = []
            for md in results["metadatas"]:
                # If data is in snake_case, convert to aliased format
                if "full_address" in md:
                    store_data = {
                        "store_id": md.get("store_id"),
                        "full_address": md.get("full_address"),
                        "geo_location_id": md.get("geo_location_id"),
                        "store_images": md.get("store_images"),
                        "store_videos": md.get("store_videos")
                    }
                    stores.append(Store(**store_data))
                else:
                    # Data already in correct format
                    stores.append(Store(**md))
            return stores

        # If Chroma has no stores, fetch from SQL
        logger.info("No stores found in Chroma, fetching from SQL database...")
        stores_from_sql = await self.fetch_stores_from_sql()

        # Store fetched data in Chroma
        for store in stores_from_sql:
            data = store.model_dump(exclude_none=True)
            doc_text = f"Store Info - {data['store_id']}: Full Address {data['full_address']}, Geo Location ID {data['geo_location_id']} reviews analyzed"
            # Generate embeddings
            embeddings = self._create_embeddings([doc_text])
            self.stores.add(ids=[data["store_id"]], metadatas=[data],
            documents=[doc_text],
            embeddings=embeddings)
        logger.info("Embedded all stores information in Chroma DB from SQL database")
        
        results = self.stores.get()
        stores = []
        for md in results["metadatas"]:
            if "full_address" in md:
                store_data = {
                    "store_id": md.get("store_id"),
                    "full_address": md.get("full_address"),
                    "geo_location_id": md.get("geo_location_id"),
                    "store_images": md.get("store_images"),
                    "store_videos": md.get("store_videos")
                }
                stores.append(Store(**store_data))
            else:
                stores.append(Store(**md))
        return stores

    async def update_store(self, store_id: str, update_data: Dict[str, Any]):
        store = await self.get_store(store_id)
        if not store:
            return
        updated = store.model_dump()
        updated.update(update_data)
        self.stores.update(ids=[store_id], metadatas=[updated])

    async def delete_store(self, store_id: str):
        self.stores.delete(ids=[store_id])

    # Sentiment Scorecard operations
    async def save_sentiment_scorecard(self, scorecard: SentimentScorecard) -> SentimentScorecard:
        data = scorecard.model_dump(exclude_none=True)
        # Convert datetime to string for ChromaDB compatibility
        if 'created_at' in data:
            data['created_at'] = data['created_at'].isoformat() if hasattr(data['created_at'], 'isoformat') else str(data['created_at'])
        doc_text = f"Sentiment scorecard for {data['store_name']}: Overall score {data['overall_score']}, {data['total_reviews_analyzed']} reviews analyzed"
        # Generate embeddings
        embeddings = self._create_embeddings([doc_text])
        self.sentiment_scorecards.add(
            ids=[data["id"]], 
            metadatas=[self._recursively_serialize_lists(data)], 
            documents=[doc_text],   
            embeddings=embeddings
        )
        return scorecard

    async def get_sentiment_scorecards(self, store_id: Optional[str] = None) -> List[SentimentScorecard]:
        results = self.sentiment_scorecards.get()
        scorecards = [SentimentScorecard(**self._recursively_deserialize_lists(md)) for md in results["metadatas"]]
        return [sc for sc in scorecards if not store_id or sc.store_name == store_id]

    # Visual Scorecard operations
    async def save_visual_scorecard(self, scorecard: VisualScorecard) -> VisualScorecard:
        data = scorecard.model_dump(exclude_none=True)
        # Convert datetime to string for ChromaDB compatibility
        if 'created_at' in data:
            data['created_at'] = data['created_at'].isoformat() if hasattr(data['created_at'], 'isoformat') else str(data['created_at'])
        doc_text = f"Visual scorecard for {data['store_name']}: Overall score {data['overall_score']}, {len(data['media_analyzed'])} files analyzed"
        # Generate embeddings
        embeddings = self._create_embeddings([doc_text])
        self.visual_scorecards.add(
            ids=[data["id"]], 
            metadatas=[self._recursively_serialize_lists(data)], 
            documents=[doc_text],
            embeddings=embeddings
        )
        return scorecard

    async def get_visual_scorecards(self, store_id: Optional[str] = None) -> List[VisualScorecard]:
        results = self.visual_scorecards.get()
        scorecards = [VisualScorecard(**self._recursively_deserialize_lists(md)) for md in results["metadatas"]]
        return [sc for sc in scorecards if not store_id or sc.store_name == store_id]

    # Alert operations
    async def create_alert(self, alert: Alert) -> Alert:
        data = alert.model_dump(exclude_none=True)
        # Convert datetime to string for ChromaDB compatibility
        if 'timestamp' in data:
            data['timestamp'] = data['timestamp'].isoformat() if hasattr(data['timestamp'], 'isoformat') else str(data['timestamp'])
        # Create text representation for document
        doc_text = f"Alert for {data['store_name']}: {data['alert_type']} - {data['description']} (Severity: {data['severity']})"
        # Generate embeddings
        embeddings = self._create_embeddings([doc_text])
        self.alerts.add(
            ids=[data["id"]],  # Use alert ID not store_id to avoid overwrites
            metadatas=[data], 
            documents=[doc_text],
            embeddings=embeddings
        )
        return alert

    async def get_alerts(self, store_id: Optional[str] = None, resolved: Optional[bool] = None) -> List[Alert]:
        results = self.alerts.get()
        alerts = [Alert(**md) for md in results["metadatas"]]
        filtered = alerts
        if store_id:
            filtered = [a for a in filtered if a.store_name == store_id]
        if resolved is not None:
            filtered = [a for a in filtered if a.resolved == resolved]
        return filtered

    async def resolve_alert(self, alert_id: str):
        alert = self.alerts.get(ids=[alert_id])
        if not alert["metadatas"]:
            return
        updated = alert["metadatas"][0]
        updated["resolved"] = True
        self.alerts.update(ids=[alert_id], metadatas=[updated])

    # Review operations
    async def save_review(self, review: Review) -> Review:
        data = review.model_dump(exclude_none=True)
        # Convert datetime to string for ChromaDB compatibility
        if 'created_at' in data:
            data['created_at'] = data['created_at'].isoformat() if hasattr(data['created_at'], 'isoformat') else str(data['created_at'])
        # Create text representation for document
        doc_text = f"Review for store {data['store_id']}: Rating {data.get('rating', 'N/A')}/5 - {data['review_text']}"
        # Generate embeddings
        embeddings = self._create_embeddings([doc_text])
        self.reviews.add(
            ids=[data["id"]],  # Use review ID not store_id to avoid overwrites
            metadatas=[data], 
            documents=[doc_text],
            embeddings=embeddings
        )
        return review

    async def get_reviews(self, store_id: Optional[str] = None) -> List[Review]:
        results = self.reviews.get()
        reviews = [Review(**md) for md in results["metadatas"]]
        return [r for r in reviews if not store_id or r.store_id == store_id]

    # Report operations
    async def save_report(self, report: ExecutiveReport) -> ExecutiveReport:
        data = report.model_dump(exclude_none=True)
        # Convert datetime to string for ChromaDB compatibility
        if 'created_at' in data:
            data['created_at'] = data['created_at'].isoformat() if hasattr(data['created_at'], 'isoformat') else str(data['created_at'])
        # Create text representation for document
        doc_text = f"Executive report for {data['store_name']} ({data['period']}): Key insights - {', '.join(data['key_insights'][:3])}"
        # Generate embeddings
        embeddings = self._create_embeddings([doc_text])
        self.reports.add(
            ids=[data["id"]],  # Use report ID not store_id to avoid overwrites
            metadatas=[self._recursively_serialize_lists(data)], 
            documents=[doc_text],
            embeddings=embeddings
        )
        return report

    async def get_reports(self, store_id: Optional[str] = None) -> List[ExecutiveReport]:
        results = self.reports.get()
        reports = [ExecutiveReport(**self._recursively_deserialize_lists(md)) for md in results["metadatas"] if md]
        return [r for r in reports if not store_id or r.store_name == store_id]


# Global database instance
chromadb = Database()
