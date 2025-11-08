# GreenPulse API Examples

This document provides practical examples for testing all GreenPulse API endpoints.

## Prerequisites

Before testing, ensure:
1. Google Earth Engine is authenticated and initialized
2. `GEE_PROJECT_ID` environment variable is set
3. (Optional) For AI assistant features:
   - `GROQ_API_KEY`: Your Groq API key
   - `GROQ_MODEL`: Your preferred Groq model (defaults to "llama2-70b-4096")

## Example Field Coordinates

For testing, you can use these sample agricultural field coordinates:

### Sample Field 1 (California Central Valley)
```json
{
  "coordinates": [
    [
      [-120.5, 37.0],
      [-120.5, 37.05],
      [-120.45, 37.05],
      [-120.45, 37.0],
      [-120.5, 37.0]
    ]
  ]
}
```

### Sample Field 2 (Iowa Corn Belt)
```json
{
  "coordinates": [
    [
      [-93.5, 42.0],
      [-93.5, 42.05],
      [-93.45, 42.05],
      [-93.45, 42.0],
      [-93.5, 42.0]
    ]
  ]
}
```

## API Endpoints Examples

### 1. Health Check

```bash
curl -X GET http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "GreenPulse Backend",
  "earth_engine_initialized": true
}
```

### 2. Yield Prediction

Analyzes field productivity and divides it into high/medium/low zones.

```bash
curl -X POST http://localhost:5000/api/yield-prediction \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [
      [
        [-120.5, 37.0],
        [-120.5, 37.05],
        [-120.45, 37.05],
        [-120.45, 37.0],
        [-120.5, 37.0]
      ]
    ],
    "start_date": "2024-09-01",
    "end_date": "2024-10-01"
  }'
```

**Response:**
```json
{
  "high_productivity_percent": 45.2,
  "medium_productivity_percent": 38.7,
  "low_productivity_percent": 16.1,
  "ndvi_stats": {
    "NDVI_mean": 0.68,
    "NDVI_min": 0.22,
    "NDVI_max": 0.89,
    "NDVI_stdDev": 0.15
  },
  "analysis_period": {
    "start_date": "2024-09-01",
    "end_date": "2024-10-01"
  }
}
```

### 3. Water Stress Detection

Identifies areas needing irrigation.

```bash
curl -X POST http://localhost:5000/api/water-stress \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [
      [
        [-120.5, 37.0],
        [-120.5, 37.05],
        [-120.45, 37.05],
        [-120.45, 37.0],
        [-120.5, 37.0]
      ]
    ],
    "start_date": "2024-10-01",
    "end_date": "2024-11-01"
  }'
```

**Response:**
```json
{
  "average_moisture_index": 0.25,
  "min_moisture_index": -0.05,
  "max_moisture_index": 0.52,
  "water_stress_area_percent": 42.3,
  "requires_irrigation": true,
  "analysis_period": {
    "start_date": "2024-10-01",
    "end_date": "2024-11-01"
  }
}
```

### 4. Crop Growth Tracking

Track crop development over time.

```bash
curl -X POST http://localhost:5000/api/crop-growth \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [
      [
        [-120.5, 37.0],
        [-120.5, 37.05],
        [-120.45, 37.05],
        [-120.45, 37.0],
        [-120.5, 37.0]
      ]
    ],
    "start_date": "2024-08-01",
    "end_date": "2024-11-01",
    "interval_days": 10
  }'
```

**Response:**
```json
{
  "time_series": [
    {"date": "2024-08-05", "ndvi": 0.42},
    {"date": "2024-08-15", "ndvi": 0.51},
    {"date": "2024-08-25", "ndvi": 0.63},
    {"date": "2024-09-04", "ndvi": 0.71},
    {"date": "2024-09-14", "ndvi": 0.75},
    {"date": "2024-09-24", "ndvi": 0.78},
    {"date": "2024-10-04", "ndvi": 0.72},
    {"date": "2024-10-14", "ndvi": 0.68},
    {"date": "2024-10-24", "ndvi": 0.61}
  ],
  "trend": "declining",
  "data_points": 9,
  "analysis_period": {
    "start_date": "2024-08-01",
    "end_date": "2024-11-01"
  }
}
```

### 5. Disease & Pest Alert

Detect vegetation anomalies indicating potential disease or pest problems.

```bash
curl -X POST http://localhost:5000/api/disease-alert \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [
      [
        [-120.5, 37.0],
        [-120.5, 37.05],
        [-120.45, 37.05],
        [-120.45, 37.0],
        [-120.5, 37.0]
      ]
    ],
    "start_date": "2024-10-15",
    "end_date": "2024-11-01"
  }'
```

**Response:**
```json
{
  "ndvi_change_mean": -0.12,
  "ndvi_change_min": -0.35,
  "ndvi_change_max": 0.08,
  "ndvi_change_stddev": 0.09,
  "anomaly_area_percent": 18.5,
  "risk_level": "high",
  "alert": true,
  "analysis_period": {
    "start_date": "2024-10-15",
    "end_date": "2024-11-01"
  }
}
```

### 6. Historical Comparison

Compare current season with past years.

```bash
curl -X POST http://localhost:5000/api/historical-comparison \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [
      [
        [-120.5, 37.0],
        [-120.5, 37.05],
        [-120.45, 37.05],
        [-120.45, 37.0],
        [-120.5, 37.0]
      ]
    ],
    "current_start": "2024-09-01",
    "current_end": "2024-10-01",
    "years_back": 1
  }'
```

**Response:**
```json
{
  "current_season": {
    "start_date": "2024-09-01",
    "end_date": "2024-10-01",
    "mean_ndvi": 0.72,
    "min_ndvi": 0.25,
    "max_ndvi": 0.88
  },
  "historical_season": {
    "start_date": "2023-09-01",
    "end_date": "2023-10-01",
    "mean_ndvi": 0.65,
    "min_ndvi": 0.22,
    "max_ndvi": 0.84
  },
  "comparison": {
    "ndvi_difference": 0.07,
    "percent_change": 10.77,
    "performance": "better"
  }
}
```

### 7. AI Assistant

Get smart recommendations based on field analysis.

```bash
curl -X POST http://localhost:5000/api/ai-assistant \
  -H "Content-Type: application/json" \
  -d '{
    "field_data": {
      "yield_prediction": {
        "high_productivity_percent": 35.2,
        "medium_productivity_percent": 42.1,
        "low_productivity_percent": 22.7,
        "ndvi_stats": {
          "NDVI_mean": 0.58
        }
      },
      "water_stress": {
        "water_stress_area_percent": 38.5,
        "average_moisture_index": 0.22,
        "requires_irrigation": true
      },
      "disease_risk": {
        "risk_level": "medium",
        "anomaly_area_percent": 8.2,
        "alert": true
      }
    },
    "query": "What actions should I take to improve my crop yield this season?"
  }'
```

**Response:**
```json
{
  "recommendation": "Based on your field analysis, here are my recommendations:\n\n1. **Immediate Irrigation**: With 38.5% of your field experiencing water stress, prioritize irrigation in the affected areas. The low moisture index (0.22) indicates significant water deficit.\n\n2. **Address Disease Risk**: The medium-level disease alert affecting 8.2% of your field requires attention. Scout these areas for visible signs of disease or pest damage. Consider targeted treatment if issues are identified.\n\n3. **Focus on Low Productivity Zones**: 22.7% of your field shows low productivity. These areas may benefit from soil testing to identify nutrient deficiencies or drainage issues.\n\n4. **Optimize Fertilization**: With a mean NDVI of 0.58, there's room for improvement. Consider variable-rate fertilizer application, focusing on medium and low productivity zones.\n\n5. **Monitor Regularly**: Continue tracking your field's progress weekly to catch any deterioration early and adjust management practices accordingly.",
  "timestamp": "2024-11-08T12:30:45.123456"
}
```

### 8. Generate Report

Create exportable reports in JSON or CSV format.

```bash
curl -X POST http://localhost:5000/api/report \
  -H "Content-Type: application/json" \
  -d '{
    "field_data": {
      "yield_prediction": {
        "high_productivity_percent": 45.2,
        "medium_productivity_percent": 38.7,
        "low_productivity_percent": 16.1
      },
      "water_stress": {
        "water_stress_area_percent": 25.3,
        "requires_irrigation": false
      }
    },
    "format": "json"
  }'
```

For CSV format, use `"format": "csv"`.

### 9. Full Field Analysis

Get comprehensive analysis with all features in one request.

```bash
curl -X POST http://localhost:5000/api/full-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "coordinates": [
      [
        [-120.5, 37.0],
        [-120.5, 37.05],
        [-120.45, 37.05],
        [-120.45, 37.0],
        [-120.5, 37.0]
      ]
    ]
  }'
```

**Response:**
```json
{
  "yield_prediction": {...},
  "water_stress": {...},
  "crop_growth": {...},
  "disease_risk": {...},
  "historical_comparison": {...},
  "summary": {
    "overall_health_score": 72.5,
    "critical_alerts": [
      "Irrigation required - significant water stress detected"
    ],
    "recommendations_count": 1
  }
}
```

## Testing with Python

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

coordinates = [
    [
        [-120.5, 37.0],
        [-120.5, 37.05],
        [-120.45, 37.05],
        [-120.45, 37.0],
        [-120.5, 37.0]
    ]
]

response = requests.post(
    f"{BASE_URL}/full-analysis",
    json={"coordinates": coordinates}
)

print(json.dumps(response.json(), indent=2))
```

## Testing with JavaScript

```javascript
const BASE_URL = "http://localhost:5000/api";

const coordinates = [
  [
    [-120.5, 37.0],
    [-120.5, 37.05],
    [-120.45, 37.05],
    [-120.45, 37.0],
    [-120.5, 37.0]
  ]
];

fetch(`${BASE_URL}/full-analysis`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ coordinates })
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

## Notes

1. **Coordinates Format**: Always provide coordinates as `[longitude, latitude]` pairs forming a closed polygon.
2. **Date Format**: Use `YYYY-MM-DD` format for all date parameters.
3. **Authentication**: Ensure Google Earth Engine is properly authenticated before making requests.
4. **Rate Limits**: Earth Engine has usage quotas. Monitor your usage in Google Cloud Console.
5. **Cloud Coverage**: Results quality depends on satellite image availability and cloud coverage for the specified dates.
