from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import logging
import sys
from pathlib import Path
from typing import List, Optional
import shutil
import json

# Add backend directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
# from database import db
from chromadb_client import chromadb as db
from models import (
    Review, AnalysisRequest, ChatQuery, WeightageUpdate,
    SentimentScorecard, VisualScorecard, Alert, ExecutiveReport
)
from database_models import Store
from agents.sentiment_analyzer import sentiment_analyzer
from agents.visual_analyzer import visual_analyzer
from agents.data_agent import data_agent
from utils.excel_handler import excel_handler
from utils.report_generator import report_generator
from data_ingestion import data_ingestion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the main app
app = FastAPI(title="Store Assistant API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ==================== Store Management ====================

@api_router.post("/stores", response_model=Store)
async def create_store(store: Store):
    """Create a new store"""
    try:
        created_store = await db.create_store(store)
        return created_store
    except Exception as e:
        logger.error(f"Error creating store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stores", response_model=List[Store], response_model_by_alias=False)
async def get_stores():
    """Get all stores"""
    try:
        stores = await db.get_all_stores()
        return stores
    except Exception as e:
        logger.error(f"Error getting stores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stores/{store_id}", response_model=Store, response_model_by_alias=False)
async def get_store(store_id: str):
    """Get a specific store"""
    try:
        store = await db.get_store(store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        return store
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Review Management ====================

@api_router.post("/reviews", response_model=Review)
async def create_review(review: Review):
    """Add a customer review"""
    try:
        created_review = await db.save_review(review)
        return created_review
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/reviews", response_model=List[Review])
async def get_reviews(store_id: Optional[str] = None):
    """Get reviews (optionally filtered by store)"""
    try:
        reviews = await db.get_reviews(store_id)
        return reviews
    except Exception as e:
        logger.error(f"Error getting reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Sentiment Analysis ====================

@api_router.post("/sentiment/analyze")
async def analyze_sentiment(
    store_id: str = Form(...),
    store_name: str = Form(...),
    weightages: Optional[str] = Form(None)
):
    """Analyze sentiment from reviews"""
    try:
        # Get reviews for the store
        reviews = await db.get_reviews(store_name)
        
        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this store")
        
        # Parse weightages if provided
        custom_weightages = None
        if weightages:
            try:
                custom_weightages = json.loads(weightages)
            except:
                pass
        
        # Analyze sentiment
        scorecard = await sentiment_analyzer.analyze_reviews(
            store_id, store_name, reviews, custom_weightages
        )
        
        # Save scorecard
        saved_scorecard = await db.save_sentiment_scorecard(scorecard)
        
        return saved_scorecard
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/sentiment/scorecards", response_model=List[SentimentScorecard])
async def get_sentiment_scorecards(store_id: Optional[str] = None):
    """Get sentiment scorecards"""
    try:
        scorecards = await db.get_sentiment_scorecards(store_id)
        return scorecards
    except Exception as e:
        logger.error(f"Error getting sentiment scorecards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Visual Analysis ====================

@api_router.post("/visual/analyze")
async def analyze_visual(
    store_id: str = Form(...),
    store_name: str = Form(...),
    files: List[UploadFile] = File(...),
    weightages: Optional[str] = Form(None)
):
    """Analyze images/videos for store metrics"""
    try:
        # Save uploaded files
        saved_files = []
        for file in files:
            file_path = config.UPLOAD_DIR / f"{store_id}_{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(str(file_path))
        
        # Parse weightages if provided
        custom_weightages = None
        if weightages:
            try:
                custom_weightages = json.loads(weightages)
            except:
                pass
        
        # Analyze visuals
        scorecard, alerts = await visual_analyzer.analyze_media(
            store_id, store_name, saved_files, custom_weightages
        )
        
        # Save scorecard
        saved_scorecard = await db.save_visual_scorecard(scorecard)
        
        # Save alerts
        for alert in alerts:
            await db.create_alert(alert)
        
        return {
            "scorecard": saved_scorecard,
            "alerts": alerts,
            "files_analyzed": len(saved_files)
        }
    except Exception as e:
        logger.error(f"Error analyzing visuals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/visual/scorecards", response_model=List[VisualScorecard])
async def get_visual_scorecards(store_id: Optional[str] = None):
    """Get visual analysis scorecards"""
    try:
        scorecards = await db.get_visual_scorecards(store_id)
        return scorecards
    except Exception as e:
        logger.error(f"Error getting visual scorecards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Alerts & Monitoring ====================

@api_router.get("/alerts", response_model=List[Alert])
async def get_alerts(store_id: Optional[str] = None, resolved: Optional[bool] = None):
    """Get alerts"""
    try:
        alerts = await db.get_alerts(store_id, resolved)
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark alert as resolved"""
    try:
        await db.resolve_alert(alert_id)
        return {"message": "Alert resolved successfully"}
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Data Agent & Chat ====================

@api_router.post("/chat/query")
async def chat_query(query: ChatQuery):
    """Natural language query interface"""
    try:
        # Gather context data
        context_data = {}
        
        if query.store_id:
            # Get store data
            store = await db.get_store(query.store_id)
            if store:
                context_data["store"] = store.model_dump()
            
            # Get latest scorecards
            sentiment_cards = await db.get_sentiment_scorecards(query.store_id)
            if sentiment_cards:
                context_data["sentiment_scorecard"] = sentiment_cards[0].model_dump()
            
            visual_cards = await db.get_visual_scorecards(query.store_id)
            if visual_cards:
                context_data["visual_scorecard"] = visual_cards[0].model_dump()
            
            # Get active alerts
            alerts = await db.get_alerts(query.store_id, resolved=False)
            context_data["active_alerts"] = [alert.model_dump() for alert in alerts]
        else:
            # Get all stores for comparison
            stores = await db.get_all_stores()
            context_data["stores"] = [store.model_dump() for store in stores]
        
        # Add custom context
        context_data.update(query.context or {})
        
        # Get response from data agent
        response = await data_agent.query(query.query, context_data)
        
        return response
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Excel Data Integration ====================

@api_router.post("/data/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """Upload Excel file with structured data"""
    try:
        # Save file
        file_path = config.UPLOAD_DIR / f"data_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read Excel data
        dataframes = excel_handler.read_excel(str(file_path))
        
        # Return summary of sheets
        summary = {
            sheet_name: {
                "rows": len(df),
                "columns": list(df.columns)
            }
            for sheet_name, df in dataframes.items()
        }
        
        return {
            "message": "Excel file uploaded successfully",
            "sheets": summary
        }
    except Exception as e:
        logger.error(f"Error uploading Excel: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Reports ====================

@api_router.post("/reports/generate")
async def generate_report(store_id: str = Form(...), store_name: str = Form(...)):
    """Generate executive report"""
    try:
        # Gather data
        sales_data = {"total_sales": 0, "avg_order_value": 0}  # Placeholder
        
        sentiment_scorecards = await db.get_sentiment_scorecards(store_id)
        sentiment_data = sentiment_scorecards[0].model_dump() if sentiment_scorecards else {}
        
        visual_scorecards = await db.get_visual_scorecards(store_id)
        visual_data = visual_scorecards[0].model_dump() if visual_scorecards else {}
        
        alerts = await db.get_alerts(store_id, resolved=False)
        alert_data = [alert.model_dump() for alert in alerts]
        
        # Generate report
        report = await report_generator.generate_executive_report(
            store_id, store_name, sales_data, sentiment_data, visual_data, alert_data
        )
        
        # Save report
        saved_report = await db.save_report(report)
        
        return saved_report
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/reports", response_model=List[ExecutiveReport])
async def get_reports(store_id: Optional[str] = None):
    """Get executive reports"""
    try:
        reports = await db.get_reports(store_id)
        return reports
    except Exception as e:
        logger.error(f"Error getting reports: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Data Ingestion & Integration ====================

@api_router.post("/data/ingest-google-reviews")
async def ingest_google_reviews(store_id: str = Form(...), store_name: str = Form(...), location: str = Form(...)):
    """Fetch Google reviews via SERP API and store with embeddings"""
    try:
        review_count = await data_ingestion.ingest_google_reviews(store_id, store_name, location)
        return {
            "message": "Google reviews ingested successfully",
            "store_id": store_id,
            "reviews_fetched": review_count
        }
    except Exception as e:
        logger.error(f"Error ingesting Google reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/data/ingest-sql-data")
async def ingest_sql_data(store_id: str = Form(...)):
    """Fetch SQL data, create embeddings, and store in ChromaDB"""
    try:
        results = await data_ingestion.ingest_sql_data_with_embeddings(store_id)
        return {
            "message": "SQL data ingested successfully",
            "store_id": store_id,
            "transactions": results.get("transactions", 0),
            "employee_shifts": results.get("employee_shifts", 0),
            "employee_info": results.get("employee_info", 0)
        }
    except Exception as e:
        logger.error(f"Error ingesting SQL data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/data/ingest-image-insights")
async def ingest_image_insights(store_id: str = Form(...), store_name: str = Form(...)):
    """Process images from Inputs folder and store insights with embeddings"""
    try:
        results = await data_ingestion.ingest_image_insights(store_id, store_name)
        return {
            "message": "Image insights ingested successfully",
            "store_id": store_id,
            "images_processed": results.get("images_processed", 0),
            "insights": results.get("insights", [])
        }
    except Exception as e:
        logger.error(f"Error ingesting image insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/data/ingest-video-insights")
async def ingest_video_insights(store_id: str = Form(...), store_name: str = Form(...)):
    """Process videos from Inputs folder and store insights with embeddings"""
    try:
        results = await data_ingestion.ingest_video_insights(store_id, store_name)
        return {
            "message": "Video insights ingested successfully",
            "store_id": store_id,
            "videos_processed": results.get("videos_processed", 0),
            "insights": results.get("insights", [])
        }
    except Exception as e:
        logger.error(f"Error ingesting video insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/data/ingest-excel-documents")
async def ingest_excel_documents():
    """Process Excel documents from Inputs folder and store with embeddings"""
    try:
        results = await data_ingestion.ingest_excel_documents()
        return {
            "message": "Excel documents ingested successfully",
            "files_processed": results.get("files_processed", 0),
            "sheets_processed": results.get("sheets_processed", 0)
        }
    except Exception as e:
        logger.error(f"Error ingesting Excel documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/data/ingest-all")
async def ingest_all_data(store_id: str = Form(...), store_name: str = Form(...), location: str = Form(...)):
    """Comprehensive data ingestion from all sources for a store"""
    try:
        results = await data_ingestion.ingest_all_data_for_store(store_id, store_name, location)
        
        # Also ingest Excel documents (store-independent)
        excel_results = await data_ingestion.ingest_excel_documents()
        results["excel_documents"] = excel_results
        
        return {
            "message": "All data ingested successfully",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in comprehensive data ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Health Check ====================

@api_router.get("/")
async def root():
    return {
        "message": "Store Assistant API",
        "version": "1.0.0",
        "status": "running",
        "azure_configured": config.is_azure_configured(),
        "serp_api_configured": config.is_serpapi_configured(),
        "chroma_db_path": config.CHROMA_DB_DIR
    }


@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "azure_openai": "configured" if config.is_azure_configured() else "not_configured",
        "serp_api": "configured" if config.is_serpapi_configured() else "not_configured",
        "chroma_db": "ready"
    }


# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_event():
    await db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
