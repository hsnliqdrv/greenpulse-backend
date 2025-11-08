from flask import Blueprint, request, jsonify, current_app
from services import EarthEngineService, AIAssistantService, ReportService
from datetime import datetime, timedelta

field_bp = Blueprint('field', __name__)
ee_service = EarthEngineService()
ai_service = AIAssistantService()
report_service = ReportService()

@field_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    app_ee_service = current_app.config.get('ee_service')
    is_initialized = app_ee_service.initialized if app_ee_service else ee_service.initialized
    
    return jsonify({
        'status': 'healthy',
        'service': 'GreenPulse Backend',
        'earth_engine_initialized': is_initialized
    })

@field_bp.route('/yield-prediction', methods=['POST'])
def yield_prediction():
    """Predict yield by analyzing field productivity zones."""
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
def water_stress_detection():
    """Detect water stress in fields."""
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
def crop_growth_tracking():
    """Track crop growth over time using NDVI time series."""
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
def disease_pest_alert():
    """Detect potential disease and pest risks."""
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
def historical_comparison():
    """Compare current season with historical data."""
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
def ai_assistant():
    """Get AI-powered recommendations based on field data."""
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
def generate_report():
    """Generate comprehensive field analysis report."""
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
    """Perform comprehensive field analysis with all features."""
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
