from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import uuid


class CustomBaseModel(BaseModel):
    
    # model dump to exclude empty lists    
    def model_dump(self, *args, **kwargs):
        original = super().model_dump(*args, **kwargs)
        return {k: v for k, v in original.items() if not (isinstance(v, (list, set, tuple)) and len(v) == 0)}
    

class Store(CustomBaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    store_name: str
    location: str
    store_code: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SentimentTheme(CustomBaseModel):
    theme: str
    score: float  # -1 to 1
    weightage: float  # 0 to 1
    sample_reviews: List[str] = []

class SentimentScorecard(CustomBaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    store_id: str
    store_name: str
    overall_score: float
    themes: List[SentimentTheme]
    total_reviews_analyzed: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class VisualMetric(CustomBaseModel):
    metric: str
    score: float  # 0 to 100
    weightage: float  # 0 to 1
    details: Union[Dict, str, Any] = {}

class VisualScorecard(CustomBaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    store_id: str
    store_name: str
    overall_score: float
    metrics: List[VisualMetric]
    media_analyzed: List[str]  # filenames
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Alert(CustomBaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    store_id: str
    store_name: str
    alert_type: str  # empty_shelves, long_queue, spill, low_staffing
    severity: str  # low, medium, high
    description: str
    media_file: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False

class Review(CustomBaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    store_id: str
    reviewer_name: Optional[str] = None
    rating: Optional[int] = None
    review_text: str
    source: str  # google, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AnalysisRequest(CustomBaseModel):
    store_id: str
    analysis_type: str  # sentiment, visual, comprehensive

class ChatQuery(CustomBaseModel):
    query: str
    store_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class WeightageUpdate(CustomBaseModel):
    metric: str
    weightage: float

class ExecutiveReport(CustomBaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    store_id: str
    store_name: str
    period: str
    sales_summary: Dict[str, Any]
    sentiment_summary: Dict[str, Any]
    visual_summary: Dict[str, Any]
    key_insights: List[str]
    recommendations: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
