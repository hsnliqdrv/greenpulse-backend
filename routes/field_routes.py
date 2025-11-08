from flask import Blueprint, request, jsonify, current_app
from services import EarthEngineService, AIAssistantService, ReportService
from datetime import datetime, timedelta
from app import require_api_key

field_bp = Blueprint('field', __name__)
ee_service = EarthEngineService()
ai_service = AIAssistantService()
report_service = ReportService()

@field_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify service status.
    ---
    tags:
      - System
    responses:
      200:
        description: Service health status
        schema:
          type: object
          properties:
            status:
              type: string
              example: "healthy"
            service:
              type: string
              example: "GreenPulse Backend"
            earth_engine_initialized:
              type: boolean
              description: Whether Google Earth Engine is properly initialized
    """
    app_ee_service = current_app.config.get('ee_service')
    is_initialized = app_ee_service.initialized if app_ee_service else ee_service.initialized
    
    return jsonify({
        'status': 'healthy',
        'service': 'GreenPulse Backend',
        'earth_engine_initialized': is_initialized
    })

@field_bp.route('/yield-prediction', methods=['POST'])
@require_api_key
def yield_prediction():
    """
    Predict yield by analyzing field productivity zones using NDVI analysis.
    ---
    tags:
      - Field Analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - coordinates
          properties:
            coordinates:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
                  minItems: 2
                  maxItems: 2
              description: Array of coordinate pairs forming a polygon
            start_date:
              type: string
              format: date
              description: Start date for analysis (default - 30 days ago)
              example: "2025-10-09"
            end_date:
              type: string
              format: date
              description: End date for analysis (default - current date)
              example: "2025-11-08"
    responses:
      200:
        description: Successful yield prediction
        schema:
          type: object
          properties:
            high_productivity_percent:
              type: number
              description: Percentage of field with high productivity
            medium_productivity_percent:
              type: number
              description: Percentage of field with medium productivity
            low_productivity_percent:
              type: number
              description: Percentage of field with low productivity
            ndvi_stats:
              type: object
              properties:
                NDVI_mean:
                  type: number
                  description: Mean NDVI value for the field
            analysis_period:
              type: object
              properties:
                start_date:
                  type: string
                  format: date
                end_date:
                  type: string
                  format: date
      400:
        description: Missing or invalid field coordinates
      500:
        description: Server error during analysis
    """
    try:
        data = request.json
        coordinates = data.get('coordinates')
        start_date = data.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        if not coordinates:
            return jsonify({'error': 'Field coordinates are required'}), 400
        
        geometry = ee_service.get_field_bounds(coordinates)
        image = ee_service.get_sentinel2_image(geometry, start_date, end_date)
        ndvi = ee_service.calculate_ndvi(image)
        
        ndvi_stats = ee_service.get_ndvi_statistics(ndvi, geometry)
        productivity_zones = ee_service.classify_productivity_zones(ndvi, geometry)
        
        result = {
            **productivity_zones,
            'ndvi_stats': ndvi_stats,
            'analysis_period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@field_bp.route('/water-stress', methods=['POST'])
@require_api_key
def water_stress_detection():
    """
    Detect water stress in fields using moisture indices.
    ---
    tags:
      - Field Analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - coordinates
          properties:
            coordinates:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
                  minItems: 2
                  maxItems: 2
              description: Array of coordinate pairs forming a polygon
            start_date:
              type: string
              format: date
              description: Start date for analysis (default - 30 days ago)
              example: "2025-10-09"
            end_date:
              type: string
              format: date
              description: End date for analysis (default - current date)
              example: "2025-11-08"
    responses:
      200:
        description: Successful water stress analysis
        schema:
          type: object
          properties:
            water_stress_area_percent:
              type: number
              description: Percentage of field showing water stress
            average_moisture_index:
              type: number
              description: Average moisture index value
            requires_irrigation:
              type: boolean
              description: Whether irrigation is recommended
            analysis_period:
              type: object
              properties:
                start_date:
                  type: string
                  format: date
                end_date:
                  type: string
                  format: date
      400:
        description: Missing or invalid field coordinates
      500:
        description: Server error during analysis
    """
    try:
        data = request.json
        coordinates = data.get('coordinates')
        start_date = data.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        if not coordinates:
            return jsonify({'error': 'Field coordinates are required'}), 400
        
        geometry = ee_service.get_field_bounds(coordinates)
        result = ee_service.detect_water_stress(geometry, start_date, end_date)
        
        result['analysis_period'] = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@field_bp.route('/crop-growth', methods=['POST'])
@require_api_key
def crop_growth_tracking():
    """
    Track crop growth over time using NDVI time series analysis.
    ---
    tags:
      - Field Analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - coordinates
          properties:
            coordinates:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
                  minItems: 2
                  maxItems: 2
              description: Array of coordinate pairs forming a polygon
            start_date:
              type: string
              format: date
              description: Start date for analysis (default - 90 days ago)
              example: "2025-08-10"
            end_date:
              type: string
              format: date
              description: End date for analysis (default - current date)
              example: "2025-11-08"
            interval_days:
              type: integer
              description: Number of days between measurements (default - 10)
              example: 10
    responses:
      200:
        description: Successful crop growth analysis
        schema:
          type: object
          properties:
            time_series:
              type: array
              items:
                type: object
                properties:
                  date:
                    type: string
                    format: date
                  ndvi:
                    type: number
            trend:
              type: string
              enum: [improving, stable, declining]
              description: Overall growth trend
            data_points:
              type: integer
              description: Number of measurements in the time series
            analysis_period:
              type: object
              properties:
                start_date:
                  type: string
                  format: date
                end_date:
                  type: string
                  format: date
      400:
        description: Missing or invalid field coordinates
      500:
        description: Server error during analysis
    """
    try:
        data = request.json
        coordinates = data.get('coordinates')
        start_date = data.get('start_date', (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'))
        end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        interval_days = data.get('interval_days', 10)
        
        if not coordinates:
            return jsonify({'error': 'Field coordinates are required'}), 400
        
        geometry = ee_service.get_field_bounds(coordinates)
        time_series = ee_service.get_time_series_ndvi(geometry, start_date, end_date, interval_days)
        
        trend = 'stable'
        if len(time_series) >= 2:
            first_ndvi = time_series[0]['ndvi']
            last_ndvi = time_series[-1]['ndvi']
            change = last_ndvi - first_ndvi
            
            if change > 0.1:
                trend = 'improving'
            elif change < -0.1:
                trend = 'declining'
        
        result = {
            'time_series': time_series,
            'trend': trend,
            'data_points': len(time_series),
            'analysis_period': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@field_bp.route('/disease-alert', methods=['POST'])
@require_api_key
def disease_pest_alert():
    """
    Detect potential disease and pest risks using vegetation analysis.
    ---
    tags:
      - Field Analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - coordinates
          properties:
            coordinates:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
                  minItems: 2
                  maxItems: 2
              description: Array of coordinate pairs forming a polygon
            start_date:
              type: string
              format: date
              description: Start date for analysis (default - 15 days ago)
              example: "2025-10-24"
            end_date:
              type: string
              format: date
              description: End date for analysis (default - current date)
              example: "2025-11-08"
    responses:
      200:
        description: Successful disease risk analysis
        schema:
          type: object
          properties:
            risk_level:
              type: string
              enum: [low, medium, high]
              description: Overall disease/pest risk level
            anomaly_area_percent:
              type: number
              description: Percentage of field showing anomalous patterns
            alert:
              type: boolean
              description: Whether immediate attention is recommended
            ndvi_change_mean:
              type: number
              description: Average NDVI change in affected areas
            analysis_period:
              type: object
              properties:
                start_date:
                  type: string
                  format: date
                end_date:
                  type: string
                  format: date
      400:
        description: Missing or invalid field coordinates
      500:
        description: Server error during analysis
    """
    try:
        data = request.json
        coordinates = data.get('coordinates')
        start_date = data.get('start_date', (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'))
        end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        if not coordinates:
            return jsonify({'error': 'Field coordinates are required'}), 400
        
        geometry = ee_service.get_field_bounds(coordinates)
        result = ee_service.detect_disease_risk(geometry, start_date, end_date)
        
        result['analysis_period'] = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@field_bp.route('/historical-comparison', methods=['POST'])
@require_api_key
def historical_comparison():
    """
    Compare current season with historical field data.
    ---
    tags:
      - Field Analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - coordinates
          properties:
            coordinates:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
                  minItems: 2
                  maxItems: 2
              description: Array of coordinate pairs forming a polygon
            current_start:
              type: string
              format: date
              description: Start date for current season (default - 30 days ago)
              example: "2025-10-09"
            current_end:
              type: string
              format: date
              description: End date for current season (default - current date)
              example: "2025-11-08"
            years_back:
              type: integer
              description: Number of years to look back for comparison (default - 1)
              example: 1
    responses:
      200:
        description: Successful historical comparison
        schema:
          type: object
          properties:
            current_season:
              type: object
              properties:
                mean_ndvi:
                  type: number
                  description: Average NDVI for current season
            historical_season:
              type: object
              properties:
                mean_ndvi:
                  type: number
                  description: Average NDVI for historical season
            comparison:
              type: object
              properties:
                performance:
                  type: string
                  enum: [better, worse, similar]
                  description: Current performance vs historical
                percent_change:
                  type: number
                  description: Percentage change in NDVI
      400:
        description: Missing or invalid field coordinates
      500:
        description: Server error during analysis
    """
    try:
        data = request.json
        coordinates = data.get('coordinates')
        current_start = data.get('current_start', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        current_end = data.get('current_end', datetime.now().strftime('%Y-%m-%d'))
        years_back = data.get('years_back', 1)
        
        if not coordinates:
            return jsonify({'error': 'Field coordinates are required'}), 400
        
        geometry = ee_service.get_field_bounds(coordinates)
        result = ee_service.compare_historical_seasons(geometry, current_start, current_end, years_back)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@field_bp.route('/ai-assistant', methods=['POST'])
@require_api_key
def ai_assistant():
    """
    Get AI-powered recommendations based on field data.
    ---
    tags:
      - AI Assistant
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - field_data
          properties:
            field_data:
              type: object
              properties:
                yield_prediction:
                  type: object
                  properties:
                    high_productivity_percent:
                      type: number
                    medium_productivity_percent:
                      type: number
                    low_productivity_percent:
                      type: number
                    ndvi_stats:
                      type: object
                water_stress:
                  type: object
                  properties:
                    water_stress_area_percent:
                      type: number
                    average_moisture_index:
                      type: number
                    requires_irrigation:
                      type: boolean
                disease_risk:
                  type: object
                  properties:
                    risk_level:
                      type: string
                    anomaly_area_percent:
                      type: number
                    alert:
                      type: boolean
            query:
              type: string
              description: Optional specific question to ask about the field data
    responses:
      200:
        description: Successful AI recommendation
        schema:
          type: object
          properties:
            recommendation:
              type: string
              description: AI-generated recommendation based on field data
            timestamp:
              type: string
              format: date-time
      400:
        description: Missing or invalid field data
      500:
        description: Server error or AI service unavailable
    """
    try:
        data = request.json
        field_data = data.get('field_data', {})
        query = data.get('query')
        
        if not field_data:
            return jsonify({'error': 'Field data is required for AI analysis'}), 400
        
        recommendation = ai_service.generate_recommendation(field_data, query)
        
        return jsonify({
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@field_bp.route('/report', methods=['POST'])
@require_api_key
def generate_report():
    """
    Generate comprehensive field analysis report in JSON or CSV format.
    ---
    tags:
      - Reports
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - field_data
          properties:
            field_data:
              type: object
              description: Field analysis data from full-analysis or individual endpoints
            format:
              type: string
              enum: [json, csv]
              default: json
              description: Desired report format
    responses:
      200:
        description: Successfully generated report
        schema:
          type: object
          properties:
            summary:
              type: object
              description: Key statistics and findings
            recommendations:
              type: array
              items:
                type: string
              description: List of actionable recommendations
            analysis_results:
              type: object
              description: Detailed analysis results
        headers:
          Content-Type:
            type: string
            description: application/json for JSON format, text/csv for CSV format
          Content-Disposition:
            type: string
            description: attachment filename for CSV format
      400:
        description: Missing or invalid field data
      500:
        description: Server error during report generation
    """
    try:
        data = request.json
        field_data = data.get('field_data', {})
        format_type = data.get('format', 'json')
        
        if not field_data:
            return jsonify({'error': 'Field data is required for report generation'}), 400
        
        summary = report_service.generate_summary_statistics(field_data)
        
        if format_type == 'csv':
            csv_report = report_service.generate_csv_report(field_data)
            return csv_report, 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=field_report.csv'}
        else:
            json_report = report_service.generate_json_report(field_data)
            return json_report, 200, {'Content-Type': 'application/json'}
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@field_bp.route('/full-analysis', methods=['POST'])
def full_field_analysis():
    """
    Perform comprehensive field analysis with all features.
    ---
    tags:
      - Field Analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - coordinates
          properties:
            coordinates:
              type: array
              items:
                type: array
                items:
                  type: array
                  items:
                    type: number
                  minItems: 2
                  maxItems: 2
              description: Array of coordinate pairs forming a polygon [[lon1,lat1], [lon2,lat2], ...]
    responses:
      200:
        description: Successful field analysis
        schema:
          type: object
          properties:
            yield_prediction:
              type: object
              properties:
                high_productivity_percent:
                  type: number
                medium_productivity_percent:
                  type: number
                low_productivity_percent:
                  type: number
                ndvi_stats:
                  type: object
            water_stress:
              type: object
              properties:
                water_stress_area_percent:
                  type: number
                average_moisture_index:
                  type: number
                requires_irrigation:
                  type: boolean
            disease_risk:
              type: object
              properties:
                risk_level:
                  type: string
                anomaly_area_percent:
                  type: number
                alert:
                  type: boolean
      400:
        description: Missing or invalid field coordinates
      500:
        description: Server error during analysis
    """
    try:
        data = request.json
        coordinates = data.get('coordinates')
        
        if not coordinates:
            return jsonify({'error': 'Field coordinates are required'}), 400
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        three_months_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        
        geometry = ee_service.get_field_bounds(coordinates)
        
        image = ee_service.get_sentinel2_image(geometry, month_ago, current_date)
        ndvi = ee_service.calculate_ndvi(image)
        
        yield_data = ee_service.classify_productivity_zones(ndvi, geometry)
        yield_data['ndvi_stats'] = ee_service.get_ndvi_statistics(ndvi, geometry)
        
        water_stress = ee_service.detect_water_stress(geometry, month_ago, current_date)
        
        crop_growth_data = ee_service.get_time_series_ndvi(geometry, three_months_ago, current_date)
        
        trend = 'stable'
        if len(crop_growth_data) >= 2:
            first_ndvi = crop_growth_data[0]['ndvi']
            last_ndvi = crop_growth_data[-1]['ndvi']
            change = last_ndvi - first_ndvi
            
            if change > 0.1:
                trend = 'improving'
            elif change < -0.1:
                trend = 'declining'
        
        disease_risk = ee_service.detect_disease_risk(geometry, month_ago, current_date)
        
        historical_comp = ee_service.compare_historical_seasons(geometry, month_ago, current_date, 1)
        
        full_analysis = {
            'yield_prediction': yield_data,
            'water_stress': water_stress,
            'crop_growth': {
                'time_series': crop_growth_data,
                'trend': trend,
                'data_points': len(crop_growth_data)
            },
            'disease_risk': disease_risk,
            'historical_comparison': historical_comp
        }
        
        summary = report_service.generate_summary_statistics(full_analysis)
        full_analysis['summary'] = summary
        
        return jsonify(full_analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
