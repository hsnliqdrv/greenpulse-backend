# GreenPulse - Agricultural Monitoring Backend

A comprehensive backend platform that provides farmers with real-time insights and recommendations using Google Earth Engine satellite data and AI-powered analysis.

## Features

### 🌾 Yield Prediction
Analyzes fields using NDVI (Normalized Difference Vegetation Index) and divides them into high, medium, and low productivity zones.

### 💧 Water Stress Detection
Identifies dry soil regions that need irrigation using soil moisture indices (NDMI).

### 📈 Crop Growth Tracking
Provides time-lapse view of crop development over weeks/months with NDVI time series data.

### 🐛 Disease & Pest Alerts
Detects unusual vegetation color patterns that may indicate disease or pest risks.

### 📊 Historical Comparison
Compares current season fields with past seasons to track performance improvements.

### 🤖 AI Assistant
Provides smart recommendations and answers farmer queries based on comprehensive field analysis using GROQ AI.

### 📋 Automated Reports
Generates detailed field analysis reports in JSON and CSV formats for easy data export.

## API Endpoints
See: [API Examples](examples/api_examples.md)

## Setup Instructions

### Prerequisites

1. **Google Cloud Project**
   - Create a Google Cloud project at https://console.cloud.google.com
   - Enable Earth Engine API
   - Note your project ID

2. **Google Earth Engine Authentication**
   - Install Earth Engine: Already installed via requirements.txt
   - Authenticate: Run `earthengine authenticate` in terminal
   - This will open a browser for Google account authentication

3. **GROQ API Key** (Optional, for AI Assistant)
  - Get an API key from your GROQ provider and set `GROQ_API_KEY`.
  - Optionally set `GROQ_API_URL` to your provider's completion endpoint.
  - Required only for `/api/ai-assistant` endpoint

### Environment Variables

Create a `.env` file in the project root:

```env
GEE_PROJECT_ID=your-google-cloud-project-id
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_URL=https://api.your-groq-provider.example/v1/complete
PORT=5000
DEBUG=False
```

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Authenticate with Earth Engine:
```bash
earthengine authenticate
```

3. Set your Google Cloud project:
```bash
earthengine set_project YOUR_PROJECT_ID
```

4. Run the application:
```bash
python app.py
```

The API will be available at `http://0.0.0.0:5000`

## Architecture

```
greenpulse-backend/
├── app.py                      # Main Flask application
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration settings
├── services/
│   ├── __init__.py
│   ├── earth_engine_service.py # Google Earth Engine integration
│   ├── ai_assistant_service.py # GROQ integration
│   └── report_service.py       # Report generation
├── routes/
│   ├── __init__.py
│   └── field_routes.py         # API route handlers
├── .env                        # Environment variables (create this)
├── .env.example               # Environment template
└── requirements.txt           # Python dependencies
```

## Technologies Used

- **Flask**: Web framework for RESTful API
- **Google Earth Engine**: Satellite imagery and geospatial analysis
 - **GROQ AI**: AI-powered agricultural recommendations
- **NumPy & Pandas**: Data processing and analysis
- **Sentinel-2**: High-resolution satellite imagery (accessed via Earth Engine)

## Satellite Imagery

The platform uses **Sentinel-2** satellite imagery which provides:
- 10m spatial resolution
- 5-day revisit time
- 13 spectral bands including NIR and SWIR for vegetation analysis

## Vegetation Indices

### NDVI (Normalized Difference Vegetation Index)
- Range: -1 to 1
- Healthy vegetation: 0.6 - 0.9
- Used for: Crop health, yield prediction, disease detection

### NDMI (Normalized Difference Moisture Index)
- Range: -1 to 1
- High moisture: > 0.3
- Used for: Water stress detection, irrigation planning

## License

Copyright © 2024 GreenInnovators

## Support

For issues or questions about the platform, please contact the development team.
