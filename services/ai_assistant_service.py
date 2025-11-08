import os
import requests
from typing import Dict, List, Optional
from config import Config
import logging

logger = logging.getLogger(__name__)


class AIAssistantService:
    """AI assistant that uses GROQ AI (configurable endpoint) or falls back to a helpful message.

    Configure via environment variables:
    - GROQ_API_KEY: the API key for GROQ.
    - GROQ_API_URL: (optional) full URL for the GROQ text-completion endpoint. If not set, the
      service will attempt a reasonable default but you may need to provide the correct endpoint
      for your GROQ account.
    """

    def __init__(self):
        self.client_key = Config.GROQ_API_KEY
        self.api_url = os.getenv('GROQ_API_URL')

    def generate_recommendation(self, field_data: Dict, query: Optional[str] = None) -> str:
        """Generate smart agricultural recommendations based on field data using GROQ.

        This implementation uses a simple HTTP call to a configurable GROQ endpoint. Because
        GROQ provider SDKs and endpoints vary, set `GROQ_API_URL` if the default does not match
        your account.
        """
        if not self.client_key:
            return "AI Assistant is not configured. Please provide GROQ_API_KEY."

        system_prompt = (
            "You are an expert agricultural advisor specializing in precision farming. "
            "You analyze field data from satellite imagery and provide actionable recommendations to farmers. "
            "Your advice should be practical, specific, and focused on improving crop yields while optimizing resource usage."
        )

        field_summary = self._prepare_field_summary(field_data)

        user_message = (
            f"Based on the following field analysis data:\n\n{field_summary}\n\n"
            + (f"User Question: {query}" if query else "Please provide comprehensive recommendations for improving crop health and yield.")
        )

        prompt = system_prompt + "\n\n" + user_message

        # Allow the environment to override the exact endpoint. If not provided, user must configure.
        if not self.api_url:
            logger.warning('GROQ_API_URL not set; using default placeholder endpoint. Set GROQ_API_URL to your provider endpoint for production.')
            # Default Groq API endpoint
            self.api_url = os.getenv('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')

        headers = {
            'Authorization': f'Bearer {self.client_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': 'llama2-70b-4096',  # or your preferred Groq model
            'messages': [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            'max_tokens': 800,
            'temperature': 0.7
        }

        try:
            logger.debug(f"Making request to Groq API at: {self.api_url}")
            logger.debug(f"Request payload: {payload}")
            
            resp = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            if not resp.ok:
                logger.error(f"Groq API error: Status {resp.status_code}, Response: {resp.text}")
                resp.raise_for_status()
                
            data = resp.json()
            logger.debug(f"Groq API response: {data}")

            # Parse Groq's response format
            if isinstance(data, dict) and 'choices' in data and len(data['choices']) > 0:
                message = data['choices'][0].get('message', {})
                if isinstance(message, dict) and 'content' in message:
                    return message['content']
            
            # If we can't parse the response in the expected format, return the raw response
            logger.warning("Unexpected response format from Groq API")
            return resp.text
            return resp.text
        except Exception as e:
            logger.error(f"Error calling GROQ API: {e}")
            return f"Error generating recommendation: {str(e)}"
    
    def _prepare_field_summary(self, field_data: Dict) -> str:
        """Prepare a readable summary of field data for the AI."""
        summary_parts = []
        
        if 'yield_prediction' in field_data:
            yp = field_data['yield_prediction']
            summary_parts.append(f"""
Yield Prediction:
- High productivity areas: {yp.get('high_productivity_percent', 0):.1f}%
- Medium productivity areas: {yp.get('medium_productivity_percent', 0):.1f}%
- Low productivity areas: {yp.get('low_productivity_percent', 0):.1f}%
- Average NDVI: {yp.get('ndvi_stats', {}).get('NDVI_mean', 0):.3f}
""")
        
        if 'water_stress' in field_data:
            ws = field_data['water_stress']
            summary_parts.append(f"""
Water Stress Analysis:
- Water stress area: {ws.get('water_stress_area_percent', 0):.1f}%
- Average moisture index: {ws.get('average_moisture_index', 0):.3f}
- Irrigation needed: {'Yes' if ws.get('requires_irrigation') else 'No'}
""")
        
        if 'disease_risk' in field_data:
            dr = field_data['disease_risk']
            summary_parts.append(f"""
Disease & Pest Risk:
- Risk level: {dr.get('risk_level', 'unknown').upper()}
- Anomaly area: {dr.get('anomaly_area_percent', 0):.1f}%
- Alert status: {'ACTIVE' if dr.get('alert') else 'None'}
- NDVI change: {dr.get('ndvi_change_mean', 0):.3f}
""")
        
        if 'historical_comparison' in field_data:
            hc = field_data['historical_comparison']
            comp = hc.get('comparison', {})
            summary_parts.append(f"""
Historical Comparison:
- Performance vs last year: {comp.get('performance', 'unknown').upper()}
- NDVI change: {comp.get('percent_change', 0):.1f}%
- Current mean NDVI: {hc.get('current_season', {}).get('mean_ndvi', 0):.3f}
- Historical mean NDVI: {hc.get('historical_season', {}).get('mean_ndvi', 0):.3f}
""")
        
        if 'crop_growth' in field_data:
            cg = field_data['crop_growth']
            if cg.get('time_series'):
                latest = cg['time_series'][-1] if cg['time_series'] else {}
                summary_parts.append(f"""
Crop Growth Tracking:
- Latest NDVI: {latest.get('ndvi', 0):.3f}
- Growth trend: {cg.get('trend', 'unknown')}
- Data points collected: {len(cg.get('time_series', []))}
""")
        
        return "\n".join(summary_parts) if summary_parts else "No field data available."
