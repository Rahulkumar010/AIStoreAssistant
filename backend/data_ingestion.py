"""
Data ingestion module for processing all data sources and creating embeddings
"""
import os
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from itertools import batched

from config import config
# from mock_data_generator import mock_data_gen
from serpapi_client import serpapi_client
from utils.sql_handler import sql_handler
from azure_openai_client import azure_client
from chromadb_client import chromadb
from models import Review
from database_models import Store, CustomerTransactions, EmployeeInfo, EmployeeShifts

logger = logging.getLogger(__name__)


class DataIngestion:
    """Handle data ingestion from multiple sources into ChromaDB with embeddings"""
    
    def __init__(self):
        self.inputs_dir = Path("C:\\Users\\rahul_thatikonda\\Desktop\\AIStoreAssistant\\Inputs")
        self.images_dir = self.inputs_dir / "Images"
        self.videos_dir = self.inputs_dir / "Videos"
        self.sample_dir = self.inputs_dir / "Sample"
    
    async def ingest_google_reviews(self, store_id: str, store_name: str, location: str) -> int:
        """
        Fetch Google reviews using SERP API and store in ChromaDB with embeddings
        For mock mode, generates realistic review data matching SERP API format
        """
        try:
            # Generate mock reviews matching SERP API format
            logger.info(f"Fetching Google reviews for {store_name}")
            # mock_reviews = mock_data_gen.generate_google_reviews(store_name, count=15)
            mock_reviews = serpapi_client.fetch_reviews(location=location)
            
            # Store reviews in ChromaDB
            review_count = 0
            for mock_review in mock_reviews:
                # Convert SERP API format to Review model
                review = Review(
                    store_id=store_name,
                    reviewer_name=mock_review["user"]["name"],
                    rating=mock_review["rating"],
                    review_text=mock_review["snippet"],
                    source=mock_review["source"]
                )
                
                # Save to ChromaDB (will automatically create embeddings)
                await chromadb.save_review(review)
                review_count += 1
            
            logger.info(f"Stored {review_count} Google reviews for {store_name}")
            return review_count
            
        except Exception as e:
            logger.error(f"Error ingesting Google reviews: {str(e)}")
            return 0
    
    async def ingest_sql_data_with_embeddings(self, store_id: str, store_name: str) -> Dict[str, int]:
        """
        Fetch structured data from SQL Server, create embeddings, and store in ChromaDB
        For mock mode, generates realistic SQL data matching database_models
        """
        try:
            logger.info(f"Generating SQL data for store {store_id}")
            
            # Generate mock transaction data matching CustomerTransactions model
            # transactions = mock_data_gen.generate_sql_transactions(store_id, count=50)
            transactions = sql_handler.query_data(table_name='dbo.customer_transactions', filters={"Store": store_name})
            
            # Create collection for transactions if not exists
            transaction_collection = chromadb.client.get_or_create_collection("transactions")
            
            # Store transactions with embeddings
            for batch in batched(transactions.iterrows(), 1000):
                ids = []
                documents = []

                for idx, transaction in batch:
                    transaction = CustomerTransactions(**transaction).model_dump()
                    # Create text representation for embedding with all relevant fields
                    text_repr = f"Transaction {transaction['transaction_id']}: Customer {transaction['customer_id']}, Age {transaction['age']}, Gender {transaction['gender']}, Income {transaction['income']}, Product: {transaction['product']} ({transaction['product_category']}), Quantity: {transaction['total_quantity']}, Unit Price: ${transaction['unit_price']}, Total: ${transaction['total_amount']}, Payment: {transaction['payment_method']}, Feedback: {transaction['customer_feedback']}, Date: {str(transaction['date'])} {str(transaction['time'])}"

                    ids.append(str(transaction['transaction_id']))
                    documents.append(text_repr)
                # Generate embedding using chromadb method (uses Azure or mock)
                embedding = chromadb._create_embeddings(documents)
                
                # Store in ChromaDB
                transaction_collection.add(
                    ids=ids,
                    embeddings=embedding,
                    # metadatas=[transaction],
                    documents=documents
                )
            
            # Generate mock employee shift data matching EmployeeShifts model
            # employee_shifts = mock_data_gen.generate_employee_data(store_id, count=20)
            employee_shifts = sql_handler.query_data(table_name='dbo.employee_shifts', filters={"Store": store_id})
            
            # Create collection for employee shifts
            employee_shifts_collection = chromadb.client.get_or_create_collection("employee_shifts")
            
            for batch in batched(employee_shifts.iterrows(), 1000):
                ids = []
                documents = []

                for idx, shift in batch:
                    shift = EmployeeShifts(**shift).model_dump()
                    text_repr = f"Employee Shift: {shift['employee_name']} (ID: {shift['employee_id']}), Role: {shift['assigned_role']}, Store: {shift['store_id']}, Date: {str(shift['date'])} ({shift['month']}), Clock In: {str(shift['clock_in'])}, Clock Out: {str(shift['clock_out'])}, Shift Duration: {str(shift['shift_hours'])}"

                    ids.append(f"{shift['employee_id']}_shift_{idx}")
                    documents.append(text_repr)

                embedding = chromadb._create_embeddings(documents)
                
                employee_shifts_collection.add(
                    ids=ids,
                    embeddings=embedding,
                    # metadatas=[shift],
                    documents=documents
                )
            
            # Generate mock employee info matching EmployeeInfo model
            # employee_info = mock_data_gen.generate_employee_info(store_id, count=10)
            employee_info = sql_handler.query_data(table_name='dbo.employee_info', filters={"Store": store_id})
            
            # Create collection for employee info
            employee_info_collection = chromadb.client.get_or_create_collection("employee_info")
            
            for batch in batched(employee_info.iterrows(), 1000):
                ids = []
                documents = []

                for idx, emp_info in batch:
                    emp_info = EmployeeInfo(**emp_info).model_dump()
                    text_repr = f"Employee: {emp_info['employee_name']} (ID: {emp_info['employee_id']}), Role: {emp_info['assigned_role']}, Store: {emp_info['store_id']}, Hire Date: {str(emp_info['hire_date'])}, Tenure: {emp_info['tenure_years']} years, Performance Rating: {emp_info['overall_employee_performance_rating']}/5"
                
                    ids.append(emp_info['employee_id'])
                    documents.append(text_repr)

                embedding = chromadb._create_embeddings(documents)
                
                employee_info_collection.add(
                    ids=ids,
                    embeddings=embedding,
                    # metadatas=[emp_info],
                    documents=documents
                )
            
            logger.info(f"Stored {len(transactions)} transactions, {len(employee_shifts)} employee shifts, and {len(employee_info)} employee info records")
            return {
                "transactions": len(transactions),
                "employee_shifts": len(employee_shifts),
                "employee_info": len(employee_info)
            }
            
        except Exception as e:
            logger.error(f"Error ingesting SQL data: {str(e)}")
            return {"transactions": 0, "employee_shifts": 0, "employee_info": 0}
    
    async def ingest_image_insights(self, store_id: str, store_name: str) -> Dict[str, Any]:
        """
        Process images from Inputs folder, generate insights, and store with embeddings
        """
        try:
            # Find images for this store
            store_folder = self.images_dir / f"Store {store_name[-1]}" if self.images_dir.exists() else None
            
            if not store_folder or not store_folder.exists():
                # Use sample images
                store_folder = self.sample_dir / "Store Images" if self.sample_dir.exists() else None
            
            if not store_folder or not store_folder.exists():
                logger.warning(f"No images found for store {store_id}")
                return {"images_processed": 0, "insights": []}
            
            image_files = list(store_folder.glob("*.jpg")) + list(store_folder.glob("*.png"))
            
            if not image_files:
                logger.warning(f"No image files found in {store_folder}")
                return {"images_processed": 0, "insights": []}
            
            logger.info(f"Processing {len(image_files)} images for store {store_id}")
            
            # Create collection for image insights
            image_collection = chromadb.client.get_or_create_collection("image_insights")
            
            insights = []
            for idx, image_path in enumerate(image_files[:5]):  # Process max 5 images
                # Generate mock analysis
                # analysis = mock_data_gen.generate_image_analysis_mock(str(image_path))
                analysis = azure_client.analyze_image(str(image_path))
                
                # Create text representation
                text_repr = f"Image analysis for {image_path.name}: Cleanliness {analysis['cleanliness']['score']}/100, Shelves {analysis['empty_shelves']['score']}/100, Queue {analysis['queue_length']['score']}/100, Staff {analysis['staff_presence']['score']}/100"
                
                # Generate embedding
                # embedding = mock_data_gen.generate_embedding_mock()
                embedding = chromadb._create_embeddings([text_repr])[0]
                
                # Store in ChromaDB
                doc_id = f"{store_id}_img_{idx}"
                image_collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    metadatas=[{
                        "store_id": store_name,
                        "store_name": store_name,
                        "image_file": image_path.name,
                        "analysis": json.dumps(analysis)
                    }],
                    documents=[text_repr]
                )
                
                insights.append({
                    "image": image_path.name,
                    "analysis": analysis
                })
            
            logger.info(f"Processed {len(insights)} images for store {store_id}")
            return {
                "images_processed": len(insights),
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error ingesting image insights: {str(e)}")
            return {"images_processed": 0, "insights": []}
    
    async def ingest_video_insights(self, store_id: str, store_name: str) -> Dict[str, Any]:
        """
        Process videos from Inputs folder, extract keyframes, analyze, and store with embeddings
        """
        try:
            # Find videos for this store
            video_files = []
            if self.videos_dir.exists():
                video_files = [f for f in self.videos_dir.glob("*.mp4") if f"Store{store_name[-1]}" in f.name]
            
            if not video_files and self.sample_dir.exists():
                video_folder = self.sample_dir / "Store Videos"
                if video_folder.exists():
                    video_files = list(video_folder.glob("*.mp4"))[:2]  # Max 2 videos
            
            if not video_files:
                logger.warning(f"No videos found for store {store_id}")
                return {"videos_processed": 0, "insights": []}
            
            logger.info(f"Processing {len(video_files)} videos for store {store_id}")
            
            # Create collection for video insights
            video_collection = chromadb.client.get_or_create_collection("video_insights")
            
            insights = []
            for idx, video_path in enumerate(video_files):
                # Generate mock video analysis (simulating keyframe analysis)
                analysis = {
                    "video_file": video_path.name,
                    "duration_seconds": random.randint(30, 180),
                    "keyframes_analyzed": random.randint(5, 10),
                    "average_scores": {
                        "cleanliness": random.randint(65, 90),
                        "queue_length": random.randint(50, 80),
                        "staff_presence": random.randint(60, 85),
                        "customer_density": random.randint(40, 90)
                    },
                    "alerts_detected": []
                }
                
                # Add alerts if scores are low
                if analysis["average_scores"]["queue_length"] < 60:
                    analysis["alerts_detected"].append("Long queues detected at multiple timestamps")
                if analysis["average_scores"]["staff_presence"] < 65:
                    analysis["alerts_detected"].append("Low staff visibility in video footage")
                
                # Create text representation
                text_repr = f"Video analysis for {video_path.name}: {analysis['keyframes_analyzed']} keyframes analyzed, avg cleanliness {analysis['average_scores']['cleanliness']}/100"
                
                # Generate embedding
                # embedding = mock_data_gen.generate_embedding_mock()
                embedding = chromadb._create_embeddings([text_repr])[0]
                
                # Store in ChromaDB
                doc_id = f"{store_id}_video_{idx}"
                video_collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    metadatas=[{
                        "store_id": store_name,
                        "store_name": store_name,
                        "video_file": video_path.name,
                        "analysis": json.dumps(analysis)
                    }],
                    documents=[text_repr]
                )
                
                insights.append(analysis)
            
            logger.info(f"Processed {len(insights)} videos for store {store_id}")
            return {
                "videos_processed": len(insights),
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error ingesting video insights: {str(e)}")
            return {"videos_processed": 0, "insights": []}
    
    async def ingest_excel_documents(self) -> Dict[str, Any]:
        """
        Process Excel documents from Inputs folder and store with embeddings
        """
        try:
            excel_files = []
            if self.sample_dir.exists():
                data_folder = self.sample_dir / "Store data"
                if data_folder.exists():
                    excel_files = list(data_folder.glob("*.xlsx"))
                    # Filter out temp files
                    excel_files = [f for f in excel_files if not f.name.startswith("~$")]
            
            if not excel_files:
                logger.warning("No Excel files found in Inputs folder")
                return {"files_processed": 0, "sheets_processed": 0}
            
            logger.info(f"Processing {len(excel_files)} Excel files")
            
            # Create collection for documents
            doc_collection = chromadb.client.get_or_create_collection("documents")
            
            total_sheets = 0
            for excel_file in excel_files[:1]:  # Process first file
                try:
                    # Read all sheets
                    excel_data = pd.ExcelFile(excel_file)
                    
                    for sheet_name in excel_data.sheet_names:
                        try:
                            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=3)
                            
                            # Create summary text
                            text_repr = f"Excel sheet '{sheet_name}' from {excel_file.name}: {len(df)} rows, columns: {', '.join(df.columns[:5].tolist())}"
                            
                            # Generate embedding
                            # embedding = mock_data_gen.generate_embedding_mock()
                            embedding = chromadb._create_embeddings([text_repr])[0]
                            
                            # Store in ChromaDB
                            doc_id = f"excel_{excel_file.stem}_{sheet_name}_{total_sheets}"
                            doc_collection.add(
                                ids=[doc_id],
                                embeddings=[embedding],
                                metadatas=[{
                                    "file_name": excel_file.name,
                                    "sheet_name": sheet_name,
                                    "row_count": len(df),
                                    "columns": json.dumps(df.columns.tolist())
                                }],
                                documents=[text_repr]
                            )
                            
                            total_sheets += 1
                        except Exception as e:
                            logger.error(f"Error processing sheet {sheet_name}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error processing Excel file {excel_file}: {str(e)}")
                    continue
            
            logger.info(f"Processed {len(excel_files)} Excel files with {total_sheets} sheets")
            return {
                "files_processed": len(excel_files),
                "sheets_processed": total_sheets
            }
            
        except Exception as e:
            logger.error(f"Error ingesting Excel documents: {str(e)}")
            return {"files_processed": 0, "sheets_processed": 0}
    
    async def ingest_all_data_for_store(self, store_id: str, store_name: str, location: str) -> Dict[str, Any]:
        """
        Comprehensive data ingestion for a store from all sources
        """
        logger.info(f"Starting comprehensive data ingestion for store {store_id}")
        
        results = {
            "store_id": store_id,
            "store_name": store_name
        }
        
        # 1. Ingest Google reviews
        review_count = await self.ingest_google_reviews(store_id, store_name, location)
        results["google_reviews"] = review_count
        
        # 2. Ingest SQL data with embeddings
        sql_data = await self.ingest_sql_data_with_embeddings(store_id, store_name)
        results["sql_data"] = sql_data
        
        # 3. Ingest image insights
        image_insights = await self.ingest_image_insights(store_id, store_name)
        results["image_insights"] = image_insights
        
        # 4. Ingest video insights
        video_insights = await self.ingest_video_insights(store_id, store_name)
        results["video_insights"] = video_insights
        
        logger.info(f"Completed data ingestion for store {store_id}")
        return results


# Global instance
data_ingestion = DataIngestion()
