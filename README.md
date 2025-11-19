# Sainsbury's Gen AI-Powered Store Assistant

## 📋 Table of Contents
- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution Architecture](#solution-architecture)
- [Technology Stack](#technology-stack)
- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Data Sources](#data-sources)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Sainsbury's Store Assistant is a Gen AI-powered solution designed to help multi-location retail store chains deliver consistent performance, superior customer experiences, and operational efficiency. The system unifies structured and unstructured data to provide comprehensive insights into store performance through an interactive conversational interface.

## 📊 Problem Statement

### Situation
In today's competitive retail environment, multi-location store chains face:
- Pressure to deliver consistent performance
- Need for superior customer experiences
- Operational efficiency challenges
- Rising costs and shifting consumer expectations

Sainsbury's collects data from numerous sources (sales systems, customer feedback, surveillance footage, inventory tools, staffing systems), but this data often remains:
- Fragmented
- Analyzed in isolation
- Rarely providing a unified picture of store performance

### Objective
Develop a Gen AI-powered Store Assistant that:
1. **Unifies Data**: Combines structured data (sales, staffing, inventory) with unstructured data (reviews, videos, images)
2. **Delivers Insights**: Analyzes key metrics (layout, queue times, staff interactions, shelf stocking)
3. **Enables Decisions**: Supports informed, data-driven decisions
4. **Monitors Visually**: Triggers alerts for issues (long queues, low staffing, empty shelves)
5. **Provides Recommendations**: Through an interactive conversational interface

---

## 🏗️ Solution Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Streamlit UI Layer                         │
│  (Dashboard, Sentiment Analysis, Visual Analysis, Monitoring)   │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Sentiment   │  │   Visual     │  │    Data      │           │
│  │   Analyzer   │  │   Analyzer   │  │    Agent     │           │
│  │   (Agent)    │  │   (Agent)    │  │   (Agent)    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────────┐
    │  Azure   │  │ ChromaDB │  │  SQL Server  │
    │  OpenAI  │  │ (Vector  │  │ (Mock/Real)  │
    │   GPT-4  │  │   DB)    │  │              │
    └──────────┘  └──────────┘  └──────────────┘
          │              │              │
          └──────────────┴──────────────┘
                         │
                         ▼
              ┌────────────────────┐
              │   Data Sources     │
              │ - Google Reviews   │
              │ - Images & Videos  │
              │ - SQL Server       │
              └────────────────────┘
```

### Agentic AI Workflow

The solution leverages **Agentic AI** patterns where specialized agents handle specific tasks:

1. **Sentiment Analyzer Agent**: Analyzes customer reviews across multiple themes
2. **Visual Analyzer Agent**: Processes images/videos for store metrics
3. **Data Agent**: Handles natural language queries and generates insights

Each agent uses Azure OpenAI's GPT-4 for intelligent reasoning and decision-making.

---

## 💻 Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **AI/ML**: Azure OpenAI (GPT-4, GPT-4 Vision)
- **Vector Database**: ChromaDB (for embeddings and semantic search)
- **Data Processing**: Pandas, OpenCV, NumPy
- **Database**: SQL Server (with mock support), ChromaDB
- **External APIs**: SERP API (for Google Reviews)

### Frontend
- **Framework**: Streamlit
- **Visualization**: Plotly, Matplotlib
- **UI Components**: Streamlit native components

### Key Libraries
```
fastapi==0.104.1
uvicorn==0.24.0
openai==1.3.0 (Azure OpenAI)
chromadb==0.4.18
streamlit==1.28.2
plotly==5.18.0
pandas==2.1.3
opencv-python==4.8.1.78
sqlalchemy==2.0.23
```

---

## 🎯 Key Features

### 1. **Sentiment Analysis from Customer Reviews**
- Web-based review analysis with sentiment scoring
- Multi-theme analysis:
  - Waiting time
  - Staff behavior
  - Cleanliness
  - Ease of locating items
  - Product availability
  - Store layout
- Customizable weightages for each theme
- Sentiment scorecard generation
- Sample review extraction per theme

### 2. **Video & Image Analysis for Insights**
- AI-powered visual analysis using GPT-4 Vision
- Metrics evaluated:
  - Store cleanliness
  - Empty shelves detection
  - Queue length monitoring
  - Staff presence tracking
  - Store organization
- Visual scorecard with customizable weightages
- Automatic keyframe extraction from videos

### 3. **Data Analyzer and Reporting**
- Natural language query interface
- Agentic workflow for data interaction
- Generates insights from structured/unstructured data
- Executive one-pager reports
- Comparative store analysis
- Performance trend identification

### 4. **Store Monitoring & Alerts**
- Real-time alert generation based on visual analysis
- Alert types:
  - Empty shelves
  - Long checkout queues
  - Low staff presence
  - Cleanliness issues
- Priority-based alert system (High, Medium, Low)
- Alert resolution tracking

### 5. **Comprehensive Data Ingestion**
- Google Reviews (via SERP API)
- SQL Server transactional data with embeddings
- Image insights from store folders
- Video insights with keyframe analysis
- Excel document processing
- All data stored with vector embeddings for semantic search

### 6. **Interactive UI with Feedback Loop**
- Intuitive Streamlit interface
- Real-time metric visualization
- Customizable weightage adjustment
- Query-based insights
- Multi-store management

---

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.11 or higher
- **Internet**: Required for Azure OpenAI API calls

### Required API Keys (for full functionality)
- Azure OpenAI API credentials
- SERP API key (for Google Reviews)
- SQL Server credentials (optional, mock mode available)

---

## 🚀 Installation & Setup

### Step 1: Clone or Extract the Repository

```bash
# Navigate to the project directory
cd /AIStoreAssistant
```

### Step 2: Create Python Virtual Environment

```bash
# Install virtual environment package
pip install virtualenv

# Create virtual environment
python -m virtualenv .venv

# Activate virtual environment
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy the template environment file:
```bash
cp .env.template backend/.env
```

2. Edit `backend/.env` with your credentials:
```bash
backend/.env  # or use your preferred editor
```

3. Configure the following variables:

```env
# Azure OpenAI Configuration (Required for AI features)
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-api-key-here"
AZURE_OPENAI_DEPLOYMENT="gpt-4"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"
AZURE_OPENAI_MODEL="gpt-4"
AZURE_EMBEDDING_MODEL="text-embedding-3-small"

# SERP API for Google Reviews (Optional)
SERP_API_KEY="your-serp-api-key"

# SQL Server Configuration (Optional - Mock mode available)
SERVER_NAME="your-sql-server"
DATABASE_NAME="sainsbury_stores"
SQL_USERNAME="your-username"
SQL_PASSWORD="your-password"

# ChromaDB Storage Path
CHROMA_DB_DIR="/app/new_app/backend/chroma_db/"

# CORS Configuration
CORS_ORIGINS="*"
```

**Note**: The application includes mock mode that works without real API keys for testing purposes.

### Step 5: Prepare Input Data

The application expects data in the `Inputs` folder:

```
Inputs/
├── Images/
│   ├── Store 1/
│   ├── Store 2/
│   └── ...
├── Videos/
│   ├── Store1-01-10-2024.mp4
│   ├── Store2-02-10-2024.mp4
│   └── ...
└── Sample/
    ├── Store Images/
    ├── Store Videos/
    └── Store data/
        └── (Excel files - if any)
```

Sample data is already included in the repository.

---

## ▶️ Running the Application

### Option 1: Run Both Services Simultaneously (Recommended)

Open **two terminal windows**:

#### Terminal 1 - Start Backend (FastAPI)
```bash
cd /AIStoreAssistant
python backend\server.py
```

The backend API will start on: `http://localhost:8001`

#### Terminal 2 - Start Frontend (Streamlit)
```bash
cd /AIStoreAssistant
streamlit run streamlit_app.py
```

The Streamlit UI will start on: `http://localhost:8501`

### Option 2: Run Services Separately

#### Start Backend Only
```bash
cd /AIStoreAssistant
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Start Frontend Only
```bash
cd /AIStoreAssistant
streamlit run streamlit_app.py
```

### Accessing the Application

1. **Frontend UI**: Open browser and navigate to `http://localhost:8501`
2. **Health Check**: Test backend at `http://localhost:8001/api/health`

---

## 📁 Project Structure

```
/AIStoreAssistant
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── data_agent.py           # Natural language query agent
│   │   ├── sentiment_analyzer.py   # Sentiment analysis agent
│   │   └── visual_analyzer.py      # Visual analysis agent
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── excel_handler.py        # Excel file processing
│   │   ├── key_frame_detector.py   # Video keyframe extraction
│   │   ├── report_generator.py     # Executive report generation
│   │   └── sql_handler.py          # SQL database operations
│   ├── azure_openai_client.py      # Azure OpenAI integration
│   ├── chromadb_client.py          # ChromaDB vector database
│   ├── config.py                   # Configuration management
│   ├── data_ingestion.py           # Multi-source data ingestion
│   ├── database.py                 # Database operations
│   ├── database_models.py          # SQL database models
│   ├── models.py                   # Pydantic data models
│   ├── mock_data_generator.py      # Mock data for testing
│   ├── serpapi_client.py           # SERP API integration
│   ├── server.py                   # FastAPI application
│   └── .env                        # Environment configuration
├── Inputs/
│   ├── Images/                     # Store images
│   ├── Videos/                     # Store videos
│   └── Sample/                     # Sample data
├── streamlit_app.py                # Streamlit UI application
├── requirements.txt                # Python dependencies
├── .env.template                   # Environment template
└── README.md                       # This file
```

---

## 📊 Data Sources

The system ingests data from multiple sources:

### 1. **Google Reviews (SERP API)**
- Fetches customer reviews from Google
- Extracts: reviewer name, rating, review text
- Generates embeddings for semantic search
- Stored in ChromaDB

### 2. **SQL Server Transactional Data**
- Transaction records (sales, products, amounts)
- Employee data (shifts, roles, performance)
- Store information
- Creates text embeddings for each record

### 3. **Images**
- Store photos from `Inputs/Images/` folder
- Analyzed using GPT-4 Vision
- Metrics: cleanliness, shelves, queues, staff, organization
- Insights stored with embeddings

### 4. **Videos**
- Store surveillance footage from `Inputs/Videos/` folder
- Keyframe extraction using OpenCV
- Each frame analyzed independently
- Aggregated scores across video

### 5. **Excel Documents - (if any)**
- Structured data from `Inputs/Sample/Store data/`
- Processes multiple sheets
- Creates searchable embeddings
- Supports sales, inventory, staffing data

---

## 🔌 API Endpoints

### Store Management
- `POST /api/stores` - Create a new store
- `GET /api/stores` - Get all stores
- `GET /api/stores/{store_id}` - Get specific store

### Reviews
- `POST /api/reviews` - Add a customer review
- `GET /api/reviews?store_id={id}` - Get reviews for a store

### Sentiment Analysis
- `POST /api/sentiment/analyze` - Analyze reviews and generate scorecard
- `GET /api/sentiment/scorecards?store_id={id}` - Get sentiment scorecards

### Visual Analysis
- `POST /api/visual/analyze` - Analyze images/videos
- `GET /api/visual/scorecards?store_id={id}` - Get visual scorecards

### Alerts & Monitoring
- `GET /api/alerts?store_id={id}&resolved={bool}` - Get alerts
- `POST /api/alerts/{alert_id}/resolve` - Resolve an alert

### Data Agent
- `POST /api/chat/query` - Natural language query

### Reports
- `POST /api/reports/generate` - Generate executive report
- `GET /api/reports?store_id={id}` - Get reports

### Data Ingestion
- `POST /api/data/ingest-google-reviews` - Ingest Google reviews
- `POST /api/data/ingest-sql-data` - Ingest SQL data with embeddings
- `POST /api/data/ingest-image-insights` - Process images
- `POST /api/data/ingest-video-insights` - Process videos
- `POST /api/data/ingest-excel-documents` - Process Excel files
- `POST /api/data/ingest-all` - Comprehensive ingestion (all sources)

### System
- `GET /api/` - API information
- `GET /api/health` - Health check

---

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|--------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL | Yes (for AI) | - |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes (for AI) | - |
| `AZURE_OPENAI_DEPLOYMENT` | GPT-4 deployment name | Yes (for AI) | gpt-4 |
| `AZURE_OPENAI_MODEL` | Model name | Yes (for AI) | gpt-4 |
| `AZURE_EMBEDDING_MODEL` | Embedding model | Yes (for AI) | text-embedding-3-small |
| `SERP_API_KEY` | SERP API key for Google reviews | No | - |
| `SERVER_NAME` | SQL Server hostname | No | - |
| `DATABASE_NAME` | SQL database name | No | - |
| `SQL_USERNAME` | SQL username | No | - |
| `SQL_PASSWORD` | SQL password | No | - |
| `CHROMA_DB_DIR` | ChromaDB storage path | Yes | ./chroma_db |
| `CORS_ORIGINS` | CORS allowed origins | No | * |

### Customizing Weightages

#### Sentiment Analysis Themes
Default weightages (customizable via UI):
- Waiting time: 20%
- Staff behavior: 25%
- Cleanliness: 15%
- Ease of locating items: 15%
- Product availability: 15%
- Store layout: 10%

#### Visual Analysis Metrics
Default weightages (customizable via UI):
- Cleanliness: 25%
- Empty shelves: 20%
- Queue length: 20%
- Staff presence: 20%
- Store organization: 15%

---

## 📖 Usage Guide

### 1. Initial Setup

1. **Start the Application** (both backend and frontend)
2. **Access the UI** at `http://localhost:8501`
3. **Create Stores**: Go to Settings → Store Management
4. **Add Store Details**: Name, Location, Store Code

### 2. Data Ingestion

1. **Navigate to**: Data Ingestion page
2. **Select a Store** from the sidebar
3. **Choose Ingestion Option**:
   - **Ingest All Data**: Processes all sources at once (recommended)
   - **Individual Sources**: Ingest data source by source
4. **Click "Ingest All Data"** and wait for completion
5. **Review Results**: Check ingestion summary

### 3. Sentiment Analysis

1. **Navigate to**: Sentiment Analysis page
2. **Add Reviews** (or use ingested Google reviews):
   - Enter review text
   - Set rating (1-5)
   - Add reviewer name (optional)
3. **Customize Weightages** (optional):
   - Expand "Customize Weightages"
   - Adjust sliders for each theme
4. **Click "Analyze Sentiment"**
5. **View Results**:
   - Overall sentiment score
   - Theme-wise breakdown
   - Sample reviews per theme

### 4. Visual Analysis

1. **Navigate to**: Visual Analysis page
2. **Upload Media**:
   - Select images/videos from your computer
   - Or use pre-loaded files from Inputs folder
3. **Customize Metric Weightages** (optional)
4. **Click "Analyze Media"**
5. **View Results**:
   - Overall visual score
   - Metric-wise breakdown
   - Alerts generated (if any)

### 5. Store Monitoring

1. **Navigate to**: Store Monitoring page
2. **View Active Alerts**:
   - High priority (red)
   - Medium priority (yellow)
   - Low priority (green)
3. **Filter Alerts**: By severity or resolved status
4. **Resolve Alerts**: Click "Resolve" button

### 6. Natural Language Queries

1. **Navigate to**: Data Analyzer page
2. **Enter Your Query**:
   - "Why is Store A performing better than Store B?"
   - "What are the main factors affecting sales?"
   - "Which stores need more staff based on queue lengths?"
3. **Select Context Store** (optional)
4. **Click "Get Insights"**
5. **Review**:
   - AI-generated response
   - Key insights
   - Recommendations

### 7. Executive Reports

1. **Navigate to**: Reports page
2. **Select a Store**
3. **Click "Generate Report"**
4. **View Report**:
   - Key insights
   - Recommendations
   - Sales summary
   - Sentiment & visual summaries

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Backend Not Starting

**Error**: `ModuleNotFoundError` or import errors

**Solution**:
```bash
# Ensure you're in the correct directory
cd /AIStoreAssistant

# Verify virtual environment is activated

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Frontend Cannot Connect to Backend

**Error**: "API Error: Connection refused"

**Solution**:
- Verify backend is running on port 8001
- Check `API_BASE_URL` in `streamlit_app.py` (line 11)
- Ensure it's set to: `http://localhost:8001/api`

#### 3. Azure OpenAI Errors

**Error**: "Azure OpenAI is not configured"

**Solution**:
- Verify `.env` file exists in `backend/` folder
- Check API key and endpoint are correct
- Test connection: `curl https://your-endpoint.openai.azure.com/`
- Application works in mock mode without real credentials

#### 4. ChromaDB Version Conflicts

**Error**: "ChromaDB version mismatch"

**Solution**:
```bash
# Delete existing ChromaDB
rm -rf /AIStoreAssistant/backend/chroma_db/

# Restart backend (will recreate database)
python backend/server.py
```

#### 6. Missing Input Files

**Error**: "No images/videos found for store"

**Solution**:
- Verify `Inputs/` folder structure exists
- Check folder names match: `Store 1`, `Store 2`, etc.
- Use sample data from `Inputs/Sample/` folder

#### 7. Excel Processing Errors

**Error**: "Error processing sheet"

**Solution**:
- Remove temporary Excel files (starting with `~$`)
- Ensure Excel files are not corrupted
- Check file permissions

### Logging

Enable debug logging for troubleshooting:

```python
# In backend/server.py, change logging level:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

- Review backend logs in terminal
- Check Streamlit console for frontend errors
- Verify all environment variables are set correctly

---

## 📄 License

This project was developed for Sainsbury's Store Assistant challenge.

---

**Version**: 1.0.0  
**Last Updated**: November 2025 
**Built with**: Azure OpenAI, FastAPI, Streamlit, ChromaDB
