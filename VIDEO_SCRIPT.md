# Sainsbury's Store Assistant - Video Walkthrough Script (5 Minutes)

---

## 🎬 VIDEO STRUCTURE

**Total Duration**: 5 Minutes  
**Target Audience**: Technical evaluators, stakeholders, retail managers  
**Tone**: Professional, clear, demonstration-focused

---

## 📝 SCRIPT

### INTRO (30 seconds)

**[Screen: Title slide with project name]**

**Narration**:

"Hello, I'm presenting the Gen AI-Powered Store Assistant solution for Sainsbury's - a comprehensive system designed to unify structured and unstructured data to deliver actionable insights for multi-location retail stores.

This 5-minute walkthrough will cover our approach, the technical architecture, and a live demonstration of key functionalities.

Let's dive in."

---

### SECTION 1: PROBLEM & APPROACH (1 minute)

**[Screen: Problem statement slide]**

**Narration**:

"The challenge: Sainsbury's collects vast amounts of data from sales systems, customer reviews, surveillance footage, and staffing systems - but this data remains fragmented and analyzed in isolation.

**[Screen: Solution architecture diagram]**

Our approach leverages Agentic AI workflows built on Azure OpenAI's GPT-4 to create three specialized intelligent agents:

1. The **Sentiment Analyzer Agent** - processes customer reviews across six themes: waiting time, staff behavior, cleanliness, product availability, ease of locating items, and store layout.

2. The **Visual Analyzer Agent** - uses GPT-4 Vision to analyze store images and videos, evaluating cleanliness, shelf stocking, queue lengths, staff presence, and store organization.

3. The **Data Agent** - enables natural language queries across all data sources, providing intelligent insights and recommendations.

**[Screen: Technology stack visualization]**

Our tech stack combines FastAPI for the backend, Streamlit for the interactive UI, ChromaDB for vector embeddings, and Azure OpenAI for AI-powered analysis. This architecture ensures scalability, maintainability, and real-time performance."

---

### SECTION 2: SYSTEM ARCHITECTURE & DATA FLOW (1 minute)

**[Screen: Architecture diagram with data flow]**

**Narration**:

"Let me walk you through the system architecture and data flow.

**[Highlight each component as mentioned]**

Data ingestion begins from five primary sources:
- Google Reviews via SERP API
- SQL Server transactional data
- Store images from the Inputs folder
- Surveillance videos
- Excel documents containing sales and operational data

**[Screen: Show data ingestion process]**

Each data source is processed through our ingestion pipeline:
1. Raw data is extracted and preprocessed
2. Text representations are created for each record
3. Azure OpenAI generates embeddings
4. Data is stored in ChromaDB for semantic search
5. Structured metadata is maintained for querying

**[Screen: Agent workflow diagram]**

When a user interacts with the system:
1. The request routes through our FastAPI backend
2. The appropriate agent is invoked
3. Relevant data is retrieved using vector similarity search
4. Azure OpenAI processes the request with context
5. Results are formatted and returned to the Streamlit UI

This architecture enables sub-second query responses even with large datasets."

---

### SECTION 3: LIVE DEMONSTRATION - KEY Features (2 minutes 30 seconds)

**[Screen: Application dashboard]**

**Narration**:

"Now, let's see the application in action.

**[Navigate to Dashboard]**

#### Part 1: Dashboard Overview (20 seconds)

"This is the main dashboard showing store performance at a glance. We see:
- Real-time sentiment and visual scores
- Active alerts count
- Store status
- Interactive scorecards for both sentiment and visual metrics
- Recent alerts with priority indicators

**[Screen: Navigate to Data Ingestion page]**

#### Part 2: Data Ingestion (25 seconds)

"The Data Ingestion page is where everything begins. Store managers can:
- Ingest Google reviews automatically
- Process SQL transactional data with embeddings
- Analyze images and videos from the Inputs folder
- Process Excel documents

With a single click on 'Ingest All Data', the system processes all sources simultaneously.

**[Click 'Ingest All Data' button - show loading]**

Watch as the system ingests reviews, processes SQL data, analyzes images, extracts video keyframes, and processes Excel sheets.

**[Screen: Show ingestion results]**

Within seconds, we've processed 15 Google reviews, 50 transactions, 10 employee records, 5 images, 2 videos, and multiple Excel sheets - all with vector embeddings for semantic search."

**[Navigate to Sentiment Analysis page]**

#### Part 3: Sentiment Analysis (30 seconds)

"Next, the Sentiment Analysis feature.

**[Screen: Show review submission interface]**

Store managers can add reviews manually or use ingested Google reviews.

**[Screen: Show weightage customization]**

A key differentiator: customizable weightages. Managers can adjust the importance of each theme based on business priorities.

For example, if 'Staff Behavior' is currently a focus area, we can increase its weightage from 25% to 35%.

**[Click 'Analyze Sentiment']**

The system processes all reviews through Azure OpenAI, analyzing sentiment across six themes.

**[Screen: Show results]**

Results include:
- An overall sentiment score
- Theme-wise breakdown with individual scores
- Sample reviews for each theme
- Visual charts for easy interpretation

This helps identify specific areas needing attention."

**[Navigate to Visual Analysis page]**

#### Part 4: Visual Analysis & Alerts (30 seconds)

"Now, Visual Analysis - arguably the most innovative feature.

**[Screen: Show file upload interface]**

Store managers upload images or videos. Our system uses GPT-4 Vision to analyze each frame.

**[Upload sample images - show processing]**

The Visual Analyzer Agent evaluates:
- Cleanliness levels
- Empty shelf detection
- Queue lengths
- Staff presence
- Store organization

**[Screen: Show visual scorecard results]**

Results show a comprehensive visual scorecard with metric breakdowns.

**[Screen: Navigate to Store Monitoring]**

Crucially, the system automatically generates alerts when metrics fall below thresholds:
- High priority: Empty shelves detected (score 30/100)
- Medium priority: Long checkout queues (score 45/100)

Store managers can view, filter, and resolve alerts in real-time."

**[Navigate to Data Analyzer page]**

#### Part 5: Natural Language Queries (25 seconds)

"Finally, the Data Analyzer - the conversational interface.

**[Screen: Show query interface]**

Store managers can ask questions in natural language:

**[Type and submit: 'Why is Store A performing better than Store B?']**

The Data Agent:
1. Retrieves relevant data using vector search
2. Analyzes performance metrics
3. Identifies key differentiators
4. Provides actionable recommendations

**[Screen: Show AI response]**

The response includes:
- A comprehensive answer
- Key insights extracted from data
- Specific recommendations
- Referenced metrics

This enables data-driven decision-making without requiring technical expertise.

**[Screen: Show example queries]**

Other example queries include comparative analysis, trend identification, and root cause analysis - all answered intelligently by our AI agents."

**[Navigate to Reports page]**

#### Part 6: Executive Reports (20 seconds)

"For executive stakeholders, the Reports feature generates comprehensive one-pagers.

**[Click 'Generate Report']**

The system compiles:
- Sales performance summary
- Sentiment analysis results
- Visual metrics
- Active alerts
- Key insights
- Actionable recommendations

**[Screen: Show generated report]**

All in a format ready for executive review - combining structured data, sentiment analysis, and visual insights in a single unified view."

---

### SECTION 4: TECHNICAL HIGHLIGHTS & CONCLUSION (30 seconds)

**[Screen: Technical highlights slide]**

**Narration**:

"Key technical highlights:

**Agentic AI Design**: Modular agents enable specialized intelligence for each task, making the system maintainable and extensible.

**Vector Embeddings**: All data is embedded using Azure OpenAI's text-embedding-3-small model, enabling semantic search across structured and unstructured sources.

**Real-time Processing**: FastAPI's async capabilities ensure sub-second responses even with complex AI operations.

**Customizable Business Logic**: Weightages can be adjusted in real-time without code changes, providing business flexibility.

**Comprehensive Monitoring**: Automatic alert generation with configurable thresholds ensures proactive issue resolution.

**[Screen: Final summary slide]**

In summary, we've built a production-ready Gen AI-powered Store Assistant that:
- Unifies fragmented data sources
- Provides actionable insights through AI agents
- Monitors stores in real-time with automated alerts
- Enables natural language querying
- Generates executive-ready reports

All built on Azure OpenAI, scalable, maintainable, and ready for deployment.

Thank you for watching. The complete codebase, documentation, and setup instructions are available in the repository."

**[Screen: End slide with contact/repo info]**

---

## 🎥 VISUAL ELEMENTS TO INCLUDE

### Screen Recordings Needed:
1. **Dashboard view** - showing metrics and scorecards
2. **Data ingestion process** - with progress indicators
3. **Sentiment analysis** - from review submission to results
4. **Visual analysis** - image upload to scorecard generation
5. **Alert monitoring** - showing different priority levels
6. **Natural language query** - full interaction flow
7. **Report generation** - from trigger to final report

### Diagrams to Show:
1. Architecture diagram with component interactions
2. Data flow visualization
3. Agentic AI workflow
4. Technology stack overview
5. Vector embedding process

### UI Screenshots:
1. Dashboard with metrics
2. Sentiment scorecard with charts
3. Visual scorecard breakdown
4. Alert management interface
5. Query results from Data Agent
6. Generated executive report

---

## 🎯 KEY POINTS TO EMPHASIZE

1. **Agentic AI Approach** - Highlight the specialized agent architecture
2. **Unified Data View** - Emphasize combining structured + unstructured data
3. **Real-time Insights** - Show speed and responsiveness
4. **Customizability** - Demonstrate weightage adjustments
5. **Production-Ready** - Mention scalability, error handling, logging
6. **Business Value** - Connect features to operational improvements

---

## 📊 PACING GUIDE

| Section | Duration | Key Focus |
|---------|----------|----------|
| Intro | 30s | Project overview |
| Problem & Approach | 1m | Architecture & agents |
| Data Flow | 1m | Technical architecture |
| Live Demo | 2m 30s | Feature demonstrations |
| Conclusion | 30s | Technical highlights |

---

## 💡 PRESENTATION TIPS

1. **Speak Clearly**: Maintain a professional, confident tone
2. **Show, Don't Just Tell**: Keep UI visible during narration
3. **Highlight Interactions**: Use cursor movements to guide viewer attention
4. **Maintain Pace**: Don't rush, but keep momentum
5. **Technical Balance**: Mix technical depth with business value
6. **Smooth Transitions**: Use clear segues between sections

---

## 🔄 BACKUP PLAN

If live demonstration fails:
- Use pre-recorded screen captures
- Show screenshots with detailed narration
- Focus more on architecture and approach
- Extend technical explanation sections

---

**Total Word Count**: ~1,500 words  
**Speaking Pace**: ~180 words/minute  
**Actual Duration**: ~5 minutes (with pauses for visuals)

---

**End of Video Script**
