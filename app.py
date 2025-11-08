from flask import Flask, jsonify
from flask_cors import CORS
from routes import field_bp
from services import EarthEngineService
from config import Config
import os

app = Flask(__name__)
CORS(app)

ee_service = EarthEngineService()

app.config['ee_service'] = ee_service

app.register_blueprint(field_bp, url_prefix='/api')

@app.before_request
def initialize_earth_engine():
    """Initialize Earth Engine before first request."""
    if not ee_service.initialized:
        project_id = Config.GEE_PROJECT_ID
        if not project_id:
            print("Warning: GEE_PROJECT_ID not set. Earth Engine may not initialize properly.")
        
        success = ee_service.initialize(project_id)
        if not success:
            print("Earth Engine initialization failed. Some features may not work.")

@app.route('/')
def home():
    """Root endpoint with API documentation."""
    return jsonify({
        'service': 'GreenPulse - Agricultural Monitoring Backend',
        'version': '1.0.0',
        'description': 'Real-time insights and recommendations for farmers using Google Earth Engine',
        'endpoints': {
            'health': 'GET /api/health - Check service health',
            'yield_prediction': 'POST /api/yield-prediction - Analyze field productivity zones',
            'water_stress': 'POST /api/water-stress - Detect water stress areas',
            'crop_growth': 'POST /api/crop-growth - Track crop growth over time',
            'disease_alert': 'POST /api/disease-alert - Detect disease and pest risks',
            'historical_comparison': 'POST /api/historical-comparison - Compare with past seasons',
            'ai_assistant': 'POST /api/ai-assistant - Get AI recommendations',
            'report': 'POST /api/report - Generate field analysis report',
            'full_analysis': 'POST /api/full-analysis - Comprehensive field analysis'
        },
        'documentation': {
            'example_coordinates': [
                [
                    [-122.4194, 37.7749],
                    [-122.4094, 37.7749],
                    [-122.4094, 37.7649],
                    [-122.4194, 37.7649],
                    [-122.4194, 37.7749]
                ]
            ],
            'note': 'Coordinates should be provided as [longitude, latitude] pairs forming a polygon'
        }
    })

if __name__ == '__main__':
    port = Config.PORT
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
