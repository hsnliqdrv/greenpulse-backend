import os
from typing import Dict, Optional
import groq
from config import Config
import logging

logger = logging.getLogger(__name__)


class AIAssistantService:
    """AI assistant that uses GROQ AI or falls back to a helpful message.

    Configure via environment variables:
    - GROQ_API_KEY: the API key for GROQ
    - GROQ_MODEL: the model to use (defaults to "llama‑3.1‑8b‑instant")
    """

    def __init__(self):
        self.client = groq.Client(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL

    def generate_recommendation(self, field_data: Dict, query: Optional[str] = None) -> str:
        """Generate smart agricultural recommendations based on field data using GROQ.
        
        Uses the official Groq Python client library to make API calls.
        """
        if not self.client:
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

        try:
            logger.debug("Making request to Groq API")
            
            # Using the official Groq client library
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            logger.debug(f"Groq API response received")
            
            # Get the response content
            if chat_completion.choices and len(chat_completion.choices) > 0:
                return chat_completion.choices[0].message.content
                
            return "No response generated from the AI model."
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
