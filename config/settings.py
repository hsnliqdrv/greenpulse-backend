import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEE_PROJECT_ID = os.getenv('GEE_PROJECT_ID')
    GEE_SERVICE_ACCOUNT_KEY = os.getenv('GEE_SERVICE_ACCOUNT_KEY')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    NDVI_THRESHOLDS = {
        'high': 0.6,
        'medium': 0.4,
        'low': 0.0
    }
    
    WATER_STRESS_THRESHOLD = 0.3
    
    DISEASE_DETECTION_SENSITIVITY = 0.15
