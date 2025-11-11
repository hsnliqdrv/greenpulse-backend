# GreenPulse API Guide

This guide provides all examples for using the GreenPulse API in one cohesive flow. Make sure your Google Earth Engine is authenticated, your `GEE_PROJECT_ID` and `API_KEY` are set, and optionally your `GROQ_API_KEY` and `GROQ_MODEL` if using AI assistant features.

All endpoints (except `/api/health`) require the header `X-API-Key: your_api_key_here`.

Sample field coordinates: `[[-120.5, 37.0], [-120.5, 37.05], [-120.45, 37.05], [-120.45, 37.0], [-120.5, 37.0]]`.

Health check: `curl -X GET http://localhost:5000/api/health` returns `{"status":"healthy","service":"GreenPulse Backend","earth_engine_initialized":true}`.

Yield prediction map: `curl -X POST http://localhost:5000/api/yield-prediction -H "X-API-Key: your_api_key_here" -H "Content-Type: application/json" -d '{"coordinates":[[[-120.5,37.0],[-120.5,37.05],[-120.45,37.05],[-120.45,37.0],[-120.5,37.0]]],"field_id":"field1"}'` returns `{"tile_url":"https://earthengine.googleapis.com/map/{mapid}/{z}/{x}/{y}?token={token}","cached":false,"description":"🌾 NDVI map: low (red), medium (yellow), high (green) productivity zones."}`.

Water stress map: `curl -X POST http://localhost:5000/api/water-stress -H "X-API-Key: your_api_key_here" -H "Content-Type: application/json" -d '{"coordinates":[[[-120.5,37.0],[-120.5,37.05],[-120.45,37.05],[-120.45,37.0],[-120.5,37.0]]],"field_id":"field1"}'` returns `{"tile_url":"https://earthengine.googleapis.com/map/{mapid}/{z}/{x}/{y}?token={token}","cached":false,"description":"💧 NDMI map showing dry (brown) and moist (blue) areas."}`.

Crop growth map: `curl -X POST http://localhost:5000/api/crop-growth -H "X-API-Key: your_api_key_here" -H "Content-Type: application/json" -d '{"coordinates":[[[-120.5,37.0],[-120.5,37.05],[-120.45,37.05],[-120.45,37.0],[-120.5,37.0]]],"field_id":"field1"}'` returns `{"tile_url":"https://earthengine.googleapis.com/map/{mapid}/{z}/{x}/{y}?token={token}","cached":false,"description":"📈 NDVI map to monitor crop development over time."}`.

Disease & pest alert map: `curl -X POST http://localhost:5000/api/disease-pest -H "X-API-Key: your_api_key_here" -H "Content-Type: application/json" -d '{"coordinates":[[[-120.5,37.0],[-120.5,37.05],[-120.45,37.05],[-120.45,37.0],[-120.5,37.0]]],"field_id":"field1"}'` returns `{"tile_url":"https://earthengine.googleapis.com/map/{mapid}/{z}/{x}/{y}?token={token}","cached":false,"description":"🐛 NDVI anomaly map showing abnormal vegetation (potential disease/pests)."}`.

Historical comparison: `curl -X POST http://localhost:5000/api/historical-comparison -H "X-API-Key: your_api_key_here" -H "Content-Type: application/json" -d '{"coordinates":[[[-120.5,37.0],[-120.5,37.05],[-120.45,37.05],[-120.45,37.0],[-120.5,37.0]]],"current_start":"2024-09-01","current_end":"2024-10-01","years_back":1}'` returns `{"current_season":{"mean_ndvi":0.72},"historical_season":{"mean_ndvi":0.65},"comparison":{"performance":"better","percent_change":10.77}}`.

AI assistant: `curl -X POST http://localhost:5000/api/ai-assistant -H "X-API-Key: your_api_key_here" -H "Content-Type: application/json" -d '{"field_data":{"yield_prediction":{"high_productivity_percent":35.2,"medium_productivity_percent":42.1,"low_productivity_percent":22.7,"ndvi_stats":{"NDVI_mean":0.58}},"water_stress":{"water_stress_area_percent":38.5,"average_moisture_index":0.22,"requires_irrigation":true},"disease_risk":{"risk_level":"medium","anomaly_area_percent":8.2,"alert":true}},"query":"What actions should I take to improve my crop yield this season?"}'` returns `{"recommendation":"Based on your field analysis, here are my recommendations: ...","timestamp":"2024-11-08T12:30:45.123456"}`.

Generate report: `curl -X POST http://localhost:5000/api/report -H "X-API-Key: your_api_key_here" -H "Content-Type: application/json" -d '{"field_data":{"yield_prediction":{"high_productivity_percent":45.2,"medium_productivity_percent":38.7,"low_productivity_percent":16.1},"water_stress":{"water_stress_area_percent":25.3,"requires_irrigation":false}},"format":"json"}'`.

Full field analysis: `curl -X POST http://localhost:5000/api/full-analysis -H "X-API-Key: your_api_key_here" -H "Content-Type: application/json" -d '{"coordinates":[[[-120.5,37.0],[-120.5,37.05],[-120.45,37.05],[-120.45,37.0],[-120.5,37.0]]]}'
returns `{"yield_prediction": {...}, "water_stress": {...}, "crop_growth": {...}, "disease_risk": {...}, "historical_comparison": {...}, "summary": {"overall_health_score":72.5,"critical_alerts":["Irrigation required - significant water stress detected"],"recommendations_count":1}}`.

Notes: always provide coordinates as `[longitude, latitude]` pairs forming a closed polygon, use `YYYY-MM-DD` format for dates, and ensure Google Earth Engine is authenticated. Tokens are cached for 1 hour; a new map URL is generated if the previous token expires.