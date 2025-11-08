# GreenPulse Agricultural Monitoring Backend

## Overview
GreenPulse is a comprehensive backend platform that provides farmers with real-time insights and recommendations using Google Earth Engine satellite data and AI-powered analysis. The platform processes Sentinel-2 satellite imagery to deliver actionable agricultural intelligence.

## Project Purpose
To give farmers timely, data-driven insights about their fields including yield predictions, water stress detection, crop growth tracking, disease alerts, and personalized AI recommendations.

## Current State
- Backend API fully implemented with Flask
- Google Earth Engine integration for satellite imagery analysis
- GROQ integration for AI-powered farming recommendations
- RESTful API endpoints for all core features
- Automated report generation (JSON/CSV formats)

## Recent Changes (2024-11-08)
- Created complete backend architecture with Flask
- Implemented Earth Engine service with NDVI and NDMI calculations
- Built yield prediction using productivity zone classification
- Added water stress detection using soil moisture indices
- Implemented crop growth tracking with time-series analysis
- Created disease and pest alert system using vegetation anomalies
- Built historical field comparison functionality
- Integrated GROQ for smart agricultural recommendations
- Added comprehensive report generation service
- Created 9 API endpoints for all features

## Project Architecture

### Core Services
1. **EarthEngineService** - Handles all Google Earth Engine operations
   - Sentinel-2 imagery retrieval
   - NDVI and NDMI calculations
   - Productivity zone classification
   - Time-series analysis
   - Anomaly detection

2. **AIAssistantService** - GROQ integration for recommendations
   - Context-aware agricultural advice
   - Field data interpretation
   - Query-based recommendations

3. **ReportService** - Automated report generation
   - JSON export
   - CSV export
   - Summary statistics

### API Endpoints
- `/api/health` - Service health check
- `/api/yield-prediction` - Field productivity analysis
- `/api/water-stress` - Irrigation needs detection
- `/api/crop-growth` - Growth tracking over time
- `/api/disease-alert` - Disease and pest risk detection
- `/api/historical-comparison` - Season-over-season analysis
- `/api/ai-assistant` - AI-powered recommendations
- `/api/report` - Report generation
- `/api/full-analysis` - Comprehensive field analysis

## Technologies
- **Backend**: Flask (Python 3.11)
- **Satellite Data**: Google Earth Engine API (Sentinel-2 imagery)
- **AI**: GROQ AI (provider configurable)
- **Data Processing**: NumPy, Pandas
- **Image Processing**: Earth Engine (cloud-based)

## Setup Requirements

### Google Earth Engine
1. Create Google Cloud project
2. Enable Earth Engine API
3. Authenticate: `earthengine authenticate`
4. Set project: `earthengine set_project YOUR_PROJECT_ID`
5. Add `GEE_PROJECT_ID` to environment variables

### GROQ (Optional - for AI Assistant)
1. Get API key from your GROQ provider
2. Add `GROQ_API_KEY` (and optionally `GROQ_API_URL`) to environment variables

## Dependencies
- flask==3.1.2
- flask-cors==6.0.1
- earthengine-api==1.6.15
 
- numpy==2.3.4
- pandas==2.3.3
- python-dotenv==1.2.1

## User Preferences
None specified yet.

## Next Steps
1. Set up Google Earth Engine authentication
2. Configure GEE_PROJECT_ID environment variable
3. (Optional) Add GROQ_API_KEY (and optionally GROQ_API_URL) for AI assistant features
4. Test API endpoints with real field coordinates
5. Consider adding webhook notifications for critical alerts
6. Implement caching layer for frequently accessed field data
