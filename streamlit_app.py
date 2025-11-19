import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from typing import List, Dict, Any
from backend.database_models import Store

# Configuration
API_BASE_URL = "http://localhost:8001/api"

# Page configuration
st.set_page_config(
    page_title="Sainsbury's Store Assistant",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6600;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .alert-high {
        background-color: #ffebee;
        padding: 1rem;
        border-left: 4px solid #f44336;
        margin-bottom: 0.5rem;
    }
    .alert-medium {
        background-color: #fff3e0;
        padding: 1rem;
        border-left: 4px solid #ff9800;
        margin-bottom: 0.5rem;
    }
    .alert-low {
        background-color: #e8f5e9;
        padding: 1rem;
        border-left: 4px solid #4caf50;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# Helper functions
def api_get(endpoint: str, params: dict = None):
    """Make GET request to API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def api_post(endpoint: str, data: dict = None, json: dict = None, files: dict = None):
    """Make POST request to API"""
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", data=data, json=json, files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def create_scorecard_chart(scorecard_data: Dict[str, Any], title: str):
    """Create scorecard visualization"""
    if not scorecard_data:
        return None
    
    themes = scorecard_data.get('themes', scorecard_data.get('metrics', []))
    
    if not themes:
        return None
    
    labels = [t.get('theme', t.get('metric', '')) for t in themes]
    scores = [t.get('score', 0) for t in themes]
    weightages = [t.get('weightage', 0) for t in themes]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels,
        y=scores,
        name='Score',
        marker_color='lightblue',
        text=[f"{s:.1f}" for s in scores],
        textposition='auto',
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Metrics",
        yaxis_title="Score",
        height=400
    )
    
    return fig


# Sidebar - Store Selection
st.sidebar.markdown("## 🏪 Store Selection")

# Get stores
stores_data = api_get("/stores")
stores = stores_data if stores_data else []

if not stores:
    st.sidebar.info("No stores found. Create a new store to get started.")
    with st.sidebar.expander("➕ Add New Store"):
        store_name = st.text_input("Store Name")
        address = st.text_input("Address")
        location = st.text_input("Store Geo Location")
        if st.button("Create Store"):
            new_store = Store(**{
                "store_id": store_name,
                "full_address": address,
                "geo_location_id": location
            })
            result = api_post("/stores", json=new_store.model_dump())
            if result:
                st.success("Store created successfully!")
                st.rerun()

selected_store = None
if stores:
    store_options = {f"{s['store_id']} ({s['full_address']})": s for s in stores}
    selected_store_name = st.sidebar.selectbox(
        "Select Store",
        options=list(store_options.keys())
    )
    selected_store = store_options[selected_store_name]

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "💭 Sentiment Analysis", "📸 Visual Analysis", 
     "💬 Data Analyzer", "🚨 Store Monitoring", "📄 Reports", "📥 Data Ingestion", "⚙️ Settings"]
)

# Main Content
st.markdown('<div class="main-header">🏪 Sainsbury\'s Store Assistant</div>', unsafe_allow_html=True)

# ==================== Dashboard Page ====================
if page == "📊 Dashboard":
    st.markdown("### Store Performance Overview")
    
    if not selected_store:
        st.info("Please select a store from the sidebar")
    else:
        store_id = selected_store['id']
        store_name = selected_store['store_id']
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Get latest scorecards
        sentiment_scorecards = api_get("/sentiment/scorecards", {"store_id": store_name})
        print(store_name, sentiment_scorecards)
        visual_scorecards = api_get("/visual/scorecards", {"store_id": store_name})
        alerts = api_get("/alerts", {"store_id": store_name, "resolved": False})
        
        sentiment_score = 0
        if sentiment_scorecards and len(sentiment_scorecards) > 0:
            sentiment_score = sentiment_scorecards[0].get('overall_score', 0)
        
        visual_score = 0
        if visual_scorecards and len(visual_scorecards) > 0:
            visual_score = visual_scorecards[0].get('overall_score', 0)
        
        col1.metric("Sentiment Score", f"{sentiment_score:.2f}")
        col2.metric("Visual Score", f"{visual_score:.1f}")
        col3.metric("Active Alerts", len(alerts) if alerts else 0)
        col4.metric("Store Status", "✅ Active")
        
        st.markdown("---")
        
        # Scorecards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💭 Sentiment Scorecard")
            if sentiment_scorecards and len(sentiment_scorecards) > 0:
                fig = create_scorecard_chart(sentiment_scorecards[0], "Customer Sentiment by Theme")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sentiment analysis available yet")
        
        with col2:
            st.markdown("#### 📸 Visual Scorecard")
            if visual_scorecards and len(visual_scorecards) > 0:
                fig = create_scorecard_chart(visual_scorecards[0], "Visual Metrics")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No visual analysis available yet")
        
        # Recent Alerts
        st.markdown("#### 🚨 Recent Alerts")
        if alerts and len(alerts) > 0:
            for alert in alerts[:5]:
                alert_class = f"alert-{alert['severity']}"
                st.markdown(
                    f'<div class="{alert_class}"><strong>{alert["alert_type"].replace("_", " ").title()}</strong><br>{alert["description"]}<br><small>{alert["timestamp"]}</small></div>',
                    unsafe_allow_html=True
                )
        else:
            st.success("No active alerts")


# ==================== Sentiment Analysis Page ====================
elif page == "💭 Sentiment Analysis":
    st.markdown("### Sentiment Analysis from Customer Reviews")
    
    if not selected_store:
        st.info("Please select a store from the sidebar")
    else:
        store_id = selected_store['id']
        store_name = selected_store['store_id']
        
        tab1, tab2 = st.tabs(["📝 Add Reviews", "📊 View Analysis"])
        
        with tab1:
            st.markdown("#### Add Customer Reviews")
            
            review_text = st.text_area("Review Text", height=150)
            col1, col2 = st.columns(2)
            reviewer_name = col1.text_input("Reviewer Name (optional)")
            rating = col2.selectbox("Rating", [1, 2, 3, 4, 5])
            source = st.text_input("Source (e.g., Google, Yelp)", value="internal")
            
            if st.button("Submit Review"):
                review_data = {
                    "store_id": store_id,
                    "reviewer_name": reviewer_name if reviewer_name else None,
                    "rating": rating,
                    "review_text": review_text,
                    "source": source
                }
                result = api_post("/reviews", json=review_data)
                if result:
                    st.success("Review submitted successfully!")
            
            st.markdown("---")
            
            # Analyze sentiment
            st.markdown("#### Run Sentiment Analysis")
            st.info("Analyzes all reviews for this store and generates a sentiment scorecard")
            
            # Weightage customization
            with st.expander("⚖️ Customize Weightages"):
                st.markdown("Adjust the importance of each theme (total should equal 1.0)")
                w_waiting = st.slider("Waiting Time", 0.0, 1.0, 0.20, 0.05)
                w_staff = st.slider("Staff Behavior", 0.0, 1.0, 0.25, 0.05)
                w_clean = st.slider("Cleanliness", 0.0, 1.0, 0.15, 0.05)
                w_location = st.slider("Ease of Locating Items", 0.0, 1.0, 0.15, 0.05)
                w_availability = st.slider("Product Availability", 0.0, 1.0, 0.15, 0.05)
                w_layout = st.slider("Store Layout", 0.0, 1.0, 0.10, 0.05)
                
                weightages = {
                    "waiting_time": w_waiting,
                    "staff_behavior": w_staff,
                    "cleanliness": w_clean,
                    "ease_of_locating_items": w_location,
                    "product_availability": w_availability,
                    "store_layout": w_layout
                }
            
            if st.button("🔍 Analyze Sentiment", type="primary"):
                with st.spinner("Analyzing reviews..."):
                    data = {
                        "store_id": store_id,
                        "store_name": store_name,
                        "weightages": json.dumps(weightages)
                    }
                    result = api_post("/sentiment/analyze", data=data)
                    if result:
                        st.success("Analysis complete!")
                        st.rerun()
        
        with tab2:
            st.markdown("#### Sentiment Analysis Results")
            
            scorecards = api_get("/sentiment/scorecards", {"store_id": store_name})
            
            if scorecards and len(scorecards) > 0:
                latest = scorecards[0]
                
                st.metric("Overall Sentiment Score", f"{latest['overall_score']:.3f}")
                st.caption(f"Based on {latest['total_reviews_analyzed']} reviews")
                
                # Chart
                fig = create_scorecard_chart(latest, "Sentiment Score by Theme")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Theme details
                st.markdown("#### Theme Breakdown")
                for theme in latest['themes']:
                    with st.expander(f"**{theme['theme'].replace('_', ' ').title()}** - Score: {theme['score']:.2f}"):
                        st.write(f"**Weightage:** {theme['weightage']:.2f}")
                        if theme['sample_reviews']:
                            st.write("**Sample Reviews:**")
                            for review in theme['sample_reviews']:
                                st.write(f"- {review}")
            else:
                st.info("No analysis results yet. Add reviews and run analysis.")


# ==================== Visual Analysis Page ====================
elif page == "📸 Visual Analysis":
    st.markdown("### Visual Analysis - Images & Videos")
    
    if not selected_store:
        st.info("Please select a store from the sidebar")
    else:
        store_id = selected_store['id']
        store_name = selected_store['store_id']
        
        tab1, tab2 = st.tabs(["📤 Upload Media", "📊 View Analysis"])
        
        with tab1:
            st.markdown("#### Upload Store Images/Videos")
            st.info("Upload images or videos of your store for AI-powered analysis")
            
            uploaded_files = st.file_uploader(
                "Choose files",
                accept_multiple_files=True,
                type=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov']
            )
            
            # Weightage customization
            with st.expander("⚖️ Customize Metric Weightages"):
                st.markdown("Adjust the importance of each metric (total should equal 1.0)")
                w_clean = st.slider("Cleanliness", 0.0, 1.0, 0.25, 0.05)
                w_shelves = st.slider("Empty Shelves", 0.0, 1.0, 0.20, 0.05)
                w_queue = st.slider("Queue Length", 0.0, 1.0, 0.20, 0.05)
                w_staff = st.slider("Staff Presence", 0.0, 1.0, 0.20, 0.05)
                w_org = st.slider("Store Organization", 0.0, 1.0, 0.15, 0.05)
                
                weightages = {
                    "cleanliness": w_clean,
                    "empty_shelves": w_shelves,
                    "queue_length": w_queue,
                    "staff_presence": w_staff,
                    "store_organization": w_org
                }
            
            if uploaded_files and st.button("🔍 Analyze Media", type="primary"):
                with st.spinner("Analyzing media files..."):
                    files = [("files", (f.name, f, f.type)) for f in uploaded_files]
                    data = {
                        "store_id": store_id,
                        "store_name": store_name,
                        "weightages": json.dumps(weightages)
                    }
                    result = api_post("/visual/analyze", data=data, files=files)
                    if result:
                        st.success(f"Analysis complete! Analyzed {result['files_analyzed']} files")
                        if result.get('alerts'):
                            st.warning(f"Generated {len(result['alerts'])} alerts")
                        st.rerun()
        
        with tab2:
            st.markdown("#### Visual Analysis Results")
            
            scorecards = api_get("/visual/scorecards", {"store_id": store_name})
            
            if scorecards and len(scorecards) > 0:
                latest = scorecards[0]
                
                st.metric("Overall Visual Score", f"{latest['overall_score']:.1f}/100")
                st.caption(f"Based on {len(latest['media_analyzed'])} media files")
                
                # Chart
                fig = create_scorecard_chart(latest, "Visual Metrics")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Metric details
                st.markdown("#### Metric Breakdown")
                cols = st.columns(2)
                for idx, metric in enumerate(latest['metrics']):
                    with cols[idx % 2]:
                        with st.expander(f"**{metric['metric'].replace('_', ' ').title()}** - {metric['score']:.1f}/100"):
                            st.write(f"**Weightage:** {metric['weightage']:.2f}")
                            if metric.get('details'):
                                st.write("**Details:**")
                                for key, value in metric['details'].items():
                                    st.write(f"- {key}: {value}")
            else:
                st.info("No analysis results yet. Upload media and run analysis.")


# ==================== Data Analyzer Page ====================
elif page == "💬 Data Analyzer":
    st.markdown("### AI-Powered Data Analyzer")
    st.info("Ask questions about store performance, compare stores, or get insights using natural language")
    
    # Query interface
    query_text = st.text_area("Enter your query:", height=100, 
                             placeholder="e.g., Why is Store A performing better than Store B?")
    
    context_store = None
    if selected_store:
        use_context = st.checkbox(f"Use {selected_store['store_id']} as context", value=True)
        if use_context:
            context_store = selected_store['id']
    
    if st.button("🔍 Get Insights", type="primary"):
        if query_text:
            with st.spinner("Analyzing..."):
                query_data = {
                    "query": query_text,
                    "store_id": context_store,
                    "context": {}
                }
                result = api_post("/chat/query", json=query_data)
                
                if result:
                    st.markdown("#### Response")
                    st.write(result.get('response', 'No response'))
                    
                    if result.get('insights'):
                        st.markdown("#### Key Insights")
                        for insight in result['insights']:
                            st.write(f"- {insight}")
                    
                    if result.get('recommendations'):
                        st.markdown("#### Recommendations")
                        for rec in result['recommendations']:
                            st.write(f"- {rec}")
        else:
            st.warning("Please enter a query")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        - **Performance Comparison:** "Compare the performance of all stores"
        - **Root Cause Analysis:** "Why are customer satisfaction scores low at Store X?"
        - **Trend Analysis:** "What are the main factors affecting sales performance?"
        - **Operational Insights:** "Which stores need more staff based on queue lengths?"
        - **Sentiment Correlation:** "How does cleanliness affect customer sentiment?"
        """)


# ==================== Store Monitoring Page ====================
elif page == "🚨 Store Monitoring":
    st.markdown("### Real-Time Store Monitoring & Alerts")
    
    if not selected_store:
        st.info("Please select a store from the sidebar or view all alerts")
        store_filter = None
    else:
        store_filter = selected_store['store_id']
    
    # Filter options
    col1, col2 = st.columns(2)
    show_resolved = col1.checkbox("Show Resolved Alerts", value=False)
    severity_filter = col2.multiselect("Severity", ["high", "medium", "low"], default=["high", "medium"])
    
    # Get alerts
    params = {}
    if store_filter:
        params["store_id"] = store_filter
    if not show_resolved:
        params["resolved"] = False
    
    alerts = api_get("/alerts", params)
    
    if alerts:
        # Filter by severity
        filtered_alerts = [a for a in alerts if a['severity'] in severity_filter]
        
        st.markdown(f"#### Active Alerts ({len(filtered_alerts)})")
        
        # Group by severity
        high_alerts = [a for a in filtered_alerts if a['severity'] == 'high']
        medium_alerts = [a for a in filtered_alerts if a['severity'] == 'medium']
        low_alerts = [a for a in filtered_alerts if a['severity'] == 'low']
        
        if high_alerts:
            st.markdown("##### 🔴 High Priority")
            for alert in high_alerts:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(
                        f'<div class="alert-high"><strong>{alert["store_name"]}</strong> - {alert["alert_type"].replace("_", " ").title()}<br>{alert["description"]}<br><small>{alert["timestamp"]}</small></div>',
                        unsafe_allow_html=True
                    )
                with col2:
                    if not alert['resolved'] and st.button("Resolve", key=f"resolve_{alert['id']}"):
                        api_post(f"/alerts/{alert['id']}/resolve")
                        st.success("Resolved!")
                        st.rerun()
        
        if medium_alerts:
            st.markdown("##### 🟡 Medium Priority")
            for alert in medium_alerts:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(
                        f'<div class="alert-medium"><strong>{alert["store_name"]}</strong> - {alert["alert_type"].replace("_", " ").title()}<br>{alert["description"]}<br><small>{alert["timestamp"]}</small></div>',
                        unsafe_allow_html=True
                    )
                with col2:
                    if not alert['resolved'] and st.button("Resolve", key=f"resolve_{alert['id']}"):
                        api_post(f"/alerts/{alert['id']}/resolve")
                        st.success("Resolved!")
                        st.rerun()
        
        if low_alerts:
            with st.expander(f"🟢 Low Priority ({len(low_alerts)})"):
                for alert in low_alerts:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(
                            f'<div class="alert-low"><strong>{alert["store_name"]}</strong> - {alert["alert_type"].replace("_", " ").title()}<br>{alert["description"]}<br><small>{alert["timestamp"]}</small></div>',
                            unsafe_allow_html=True
                        )
                    with col2:
                        if not alert['resolved'] and st.button("Resolve", key=f"resolve_{alert['id']}"):
                            api_post(f"/alerts/{alert['id']}/resolve")
                            st.success("Resolved!")
                            st.rerun()
    else:
        st.success("✅ No active alerts")


# ==================== Reports Page ====================
elif page == "📄 Reports":
    st.markdown("### Executive Reports")
    
    if not selected_store:
        st.info("Please select a store from the sidebar")
    else:
        store_id = selected_store['id']
        store_name = selected_store['store_id']
        
        tab1, tab2 = st.tabs(["📊 Generate Report", "📑 View Reports"])
        
        with tab1:
            st.markdown("#### Generate Executive One-Pager Report")
            st.info("Generates a comprehensive report combining sales data, sentiment analysis, visual metrics, and alerts")
            
            if st.button("📄 Generate Report", type="primary"):
                with st.spinner("Generating report..."):
                    data = {
                        "store_id": store_id,
                        "store_name": store_name
                    }
                    result = api_post("/reports/generate", data=data)
                    if result:
                        st.success("Report generated successfully!")
                        st.rerun()
        
        with tab2:
            st.markdown("#### Generated Reports")
            
            reports = api_get("/reports", {"store_id": store_name})
            
            if reports and len(reports) > 0:
                for report in reports:
                    with st.expander(f"Report - {report['period']} ({report['created_at']})"):
                        st.markdown("##### Key Insights")
                        for insight in report['key_insights']:
                            st.write(f"- {insight}")
                        
                        st.markdown("##### Recommendations")
                        for rec in report['recommendations']:
                            st.write(f"- {rec}")
                        
                        # Sales summary
                        if report.get('sales_summary'):
                            st.markdown("##### Sales Summary")
                            st.json(report['sales_summary'])
            else:
                st.info("No reports generated yet")


# ==================== Data Ingestion Page ====================
elif page == "📥 Data Ingestion":
    st.markdown("### Comprehensive Data Ingestion")
    st.info("Ingest data from multiple sources: Google Reviews (SERP API), SQL Server, Images, Videos, and Excel Documents")
    
    if not selected_store:
        st.warning("Please select a store from the sidebar to ingest data")
    else:
        store_id = selected_store['id']
        store_name = selected_store['store_id']
        location = selected_store['full_address']
        
        tab1, tab2, tab3 = st.tabs(["🔄 Ingest All Data", "📊 Individual Sources", "📈 Ingestion Status"])
        
        with tab1:
            st.markdown("#### Ingest All Data Sources")
            st.write(f"**Store:** {store_name}")
            st.write(f"**Location:** {location}")
            
            st.markdown("""
            This will ingest data from all sources:
            - ✅ Google Reviews via SERP API
            - ✅ SQL Server transactional data with embeddings
            - ✅ Image insights from Inputs folder
            - ✅ Video insights from Inputs folder
            - ✅ Excel documents processing
            """)
            
            if st.button("🚀 Ingest All Data", type="primary"):
                with st.spinner("Processing all data sources... This may take a few minutes."):
                    data = {
                        "store_id": store_id,
                        "store_name": store_name,
                        "location": location
                    }
                    result = api_post("/data/ingest-all", data=data)
                    
                    if result:
                        st.success("✅ All data ingested successfully!")
                        
                        # Display results
                        st.markdown("#### Ingestion Summary")
                        results = result.get("results", {})
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Google Reviews", results.get("google_reviews", 0))
                        col2.metric("SQL Transactions", results.get("sql_data", {}).get("transactions", 0))
                        col3.metric("Employee Shifts", results.get("sql_data", {}).get("employee_shifts", 0))
                        
                        col4, col5, col6 = st.columns(3)
                        col4.metric("Images Processed", results.get("image_insights", {}).get("images_processed", 0))
                        col5.metric("Videos Processed", results.get("video_insights", {}).get("videos_processed", 0))
                        col6.metric("Excel Sheets", results.get("excel_documents", {}).get("sheets_processed", 0))
        
        with tab2:
            st.markdown("#### Individual Data Sources")
            
            # Google Reviews
            st.markdown("##### 📝 Google Reviews (SERP API)")
            if st.button("Ingest Google Reviews"):
                with st.spinner("Fetching reviews from Google..."):
                    data = {
                        "store_id": store_id,
                        "store_name": store_name,
                        "location": location
                    }
                    result = api_post("/data/ingest-google-reviews", data=data)
                    if result:
                        st.success(f"Fetched {result.get('reviews_fetched', 0)} reviews")
            
            st.markdown("---")
            
            # SQL Data
            st.markdown("##### 💾 SQL Server Data")
            if st.button("Ingest SQL Data with Embeddings"):
                with st.spinner("Processing SQL data..."):
                    data = {"store_id": store_name}
                    result = api_post("/data/ingest-sql-data", data=data)
                    if result:
                        st.success(f"Processed {result.get('transactions', 0)} transactions, {result.get('employee_shifts', 0)} employee shifts, and {result.get('employee_info', 0)} employee info records")
            
            st.markdown("---")
            
            # Image Insights
            st.markdown("##### 📸 Image Insights")
            if st.button("Process Images from Inputs Folder"):
                with st.spinner("Analyzing images..."):
                    data = {
                        "store_id": store_id,
                        "store_name": store_name
                    }
                    result = api_post("/data/ingest-image-insights", data=data)
                    if result:
                        st.success(f"Processed {result.get('images_processed', 0)} images")
                        if result.get('insights'):
                            st.markdown("**Sample Insights:**")
                            for insight in result['insights'][:2]:
                                st.write(f"- {insight['image']}: Cleanliness {insight['analysis']['cleanliness']['score']}/100")
            
            st.markdown("---")
            
            # Video Insights
            st.markdown("##### 🎥 Video Insights")
            if st.button("Process Videos from Inputs Folder"):
                with st.spinner("Analyzing videos..."):
                    data = {
                        "store_id": store_id,
                        "store_name": store_name
                    }
                    result = api_post("/data/ingest-video-insights", data=data)
                    if result:
                        st.success(f"Processed {result.get('videos_processed', 0)} videos")
            
            st.markdown("---")
            
            # Excel Documents
            st.markdown("##### 📄 Excel Documents")
            if st.button("Process Excel Documents"):
                with st.spinner("Processing Excel files..."):
                    result = api_post("/data/ingest-excel-documents", data={})
                    if result:
                        st.success(f"Processed {result.get('sheets_processed', 0)} sheets from {result.get('files_processed', 0)} files")
        
        with tab3:
            st.markdown("#### ChromaDB Collections Status")
            st.info("View the status of data stored in ChromaDB vector database")
            
            # Display collection info
            health = api_get("/health")
            if health:
                st.json(health)


# ==================== Settings Page ====================
elif page == "⚙️ Settings":
    st.markdown("### Settings & Configuration")
    
    tab1, tab2, tab3 = st.tabs(["🔑 Azure OpenAI", "📤 Data Upload", "🏪 Store Management"])
    
    with tab1:
        st.markdown("#### Azure OpenAI Configuration")
        st.info("Configure Azure OpenAI credentials for AI-powered analysis")
        
        # Check current configuration status
        health = api_get("/health")
        if health:
            if health.get('azure_openai') == 'configured':
                st.success("✅ Azure OpenAI is configured")
            else:
                st.warning("⚠️ Azure OpenAI is not configured")
        
        with st.form("azure_config"):
            st.text_input("Azure OpenAI Endpoint", placeholder="https://your-resource.openai.azure.com/")
            st.text_input("API Key", type="password")
            st.text_input("API Version", value="2024-02-15-preview")
            st.text_input("GPT-4 Deployment Name", value="gpt-4")
            st.text_input("GPT-4 Vision Deployment Name", value="gpt-4-vision")
            
            if st.form_submit_button("💾 Save Configuration"):
                st.info("Configuration update feature coming soon. Please update .env file directly.")
    
    with tab2:
        st.markdown("#### Upload Structured Data (Excel)")
        st.info("Upload Excel files containing sales, staff, location, or transactional data")
        
        excel_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'])
        
        if excel_file and st.button("📤 Upload"):
            with st.spinner("Uploading and processing..."):
                files = [("file", (excel_file.name, excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))]
                result = api_post("/data/upload-excel", files=files)
                if result:
                    st.success("File uploaded successfully!")
                    if result.get('sheets'):
                        st.markdown("##### Sheets Processed:")
                        for sheet_name, info in result['sheets'].items():
                            st.write(f"- **{sheet_name}**: {info['rows']} rows, {len(info['columns'])} columns")
    
    with tab3:
        st.markdown("#### Store Management")
        
        # Add new store
        with st.expander("➕ Add New Store"):
            with st.form("new_store"):
                store_name = st.text_input("Store Name")
                address = st.text_input("Address")
                location = st.text_input("Store Geo Location")
                
                if st.form_submit_button("Create Store"):
                    new_store = Store(**{
                        "store_id": store_name,
                        "full_address": address,
                        "geo_location_id": location
                    })
                    result = api_post("/stores", json=new_store.model_dump())
                    if result:
                        st.success("Store created successfully!")
                        st.rerun()
        
        # List existing stores
        st.markdown("##### Existing Stores")
        if stores:
            for store in stores:
                st.write(f"- **{store['store_id']}** ({store['full_address']}) - Geo Location: {store['geo_location_id']}")
        else:
            st.info("No stores found")


# Footer
st.markdown("---")
st.markdown("© 2025 Sainsbury's Store Assistant | Powered by Azure OpenAI")
