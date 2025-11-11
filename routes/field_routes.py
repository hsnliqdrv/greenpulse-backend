from flask import Blueprint, request, jsonify, current_app
from services import EarthEngineService, AIAssistantService, ReportService
from datetime import datetime, timedelta
from auth import require_api_key
from flasgger import swag_from

MAP_CACHE = {}
TOKEN_LIFETIME_HOURS = 1

def get_cached_map(field_id, map_type):
    key = (field_id, map_type)
    entry = MAP_CACHE.get(key)
    if entry:
        age = (datetime.now() - entry['created']).total_seconds() / 3600
        if age < TOKEN_LIFETIME_HOURS:
            return entry
        else:
            del MAP_CACHE[key]
    return None

def cache_map(field_id, map_type, mapid, token):
    MAP_CACHE[(field_id, map_type)] = {
        'mapid': mapid,
        'token': token,
        'created': datetime.now()
    }

field_bp = Blueprint('field', __name__)
ee_service = EarthEngineService()
ai_service = AIAssistantService()
report_service = ReportService()


@field_bp.route('/health', methods=['GET'])
@swag_from({
    'tags': ['Health'],
    'responses': {
        200: {
            'description': 'Service health status',
            'examples': {
                'application/json': {
                    'status': 'healthy',
                    'service': 'GreenPulse Backend',
                    'earth_engine_initialized': True
                }
            }
        }
    }
})
def health_check():
    app_ee_service = current_app.config.get('ee_service')
    is_initialized = app_ee_service.initialized if app_ee_service else ee_service.initialized
    return jsonify({
        'status': 'healthy',
        'service': 'GreenPulse Backend',
        'earth_engine_initialized': is_initialized
    })


def _generate_map_url(field_id, map_type, coordinates, image_func, vis):
    cached = get_cached_map(field_id, map_type)
    if cached:
        mapid = cached['mapid']
        token = cached.get('token')
        base_url = f"https://earthengine.googleapis.com/v1alpha/projects/greenpulse-backend/maps/{mapid}/tiles/{{z}}/{{x}}/{{y}}"
        return f"{base_url}?token={token}" if token else base_url

    geometry = ee_service.get_field_bounds(coordinates)
    image = image_func(geometry)
    map_id = image.getMapId(vis)
    mapid = map_id['mapid']
    token = map_id.get('token')
    cache_map(field_id, map_type, mapid, token)

    base_url = f"https://earthengine.googleapis.com/v1alpha/projects/greenpulse-backend/maps/{mapid}/tiles/{{z}}/{{x}}/{{y}}"
    return f"{base_url}?token={token}" if token else base_url


def _default_dates():
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    return start_date, end_date


@field_bp.route('/yield-prediction', methods=['POST'])
@require_api_key
@swag_from({
    'tags': ['Maps'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'coordinates': {'type': 'array', 'items': {'type': 'array'}},
                    'field_id': {'type': 'string'}
                },
                'required': ['coordinates']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'NDVI yield prediction map URL',
            'examples': {
                'application/json': {
                    'tile_url': 'https://earthengine.googleapis.com/v1alpha/projects/.../tiles/{z}/{x}/{y}?token=XYZ',
                    'description': '🌾 NDVI map: low (red), medium (yellow), high (green) productivity zones.'
                }
            }
        },
        400: {'description': 'Coordinates are required'}
    }
})
def yield_prediction_map():
    data = request.json
    coordinates = data.get('coordinates')
    field_id = data.get('field_id', 'default')
    if not coordinates:
        return jsonify({'error': 'Coordinates are required'}), 400

    start_date, end_date = _default_dates()

    def image_func(geom):
        image = ee_service.get_sentinel2_image(geom, start_date, end_date)
        return ee_service.calculate_ndvi(image)

    vis = {"min": 0, "max": 1, "palette": ["red", "yellow", "green"]}
    tile_url = _generate_map_url(field_id, 'yield_prediction', coordinates, image_func, vis)
    return jsonify({
        "tile_url": tile_url,
        "description": "🌾 NDVI map: low (red), medium (yellow), high (green) productivity zones."
    })


@field_bp.route('/water-stress', methods=['POST'])
@require_api_key
@swag_from({
    'tags': ['Maps'],
    'parameters': [
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {'type': 'object', 'properties': {'coordinates': {'type': 'array'}, 'field_id': {'type': 'string'}}, 'required': ['coordinates']}}
    ],
    'responses': {
        200: {'description': 'Water stress map URL'},
        400: {'description': 'Coordinates are required'}
    }
})
def water_stress_map():
    data = request.json
    coordinates = data.get('coordinates')
    field_id = data.get('field_id', 'default')
    if not coordinates:
        return jsonify({'error': 'Coordinates are required'}), 400

    start_date, end_date = _default_dates()

    def image_func(geom):
        image = ee_service.get_sentinel2_image(geom, start_date, end_date)
        ndmi = image.normalizedDifference(['B8', 'B11']).rename('NDMI')
        return ndmi

    vis = {"min": -1, "max": 1, "palette": ["brown", "yellow", "blue"]}
    tile_url = _generate_map_url(field_id, 'water_stress', coordinates, image_func, vis)
    return jsonify({
        "tile_url": tile_url,
        "description": "💧 NDMI map showing dry (brown) and moist (blue) areas."
    })


@field_bp.route('/crop-growth', methods=['POST'])
@require_api_key
@swag_from({
    'tags': ['Maps'],
    'parameters': [
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {'type': 'object', 'properties': {'coordinates': {'type': 'array'}, 'field_id': {'type': 'string'}}, 'required': ['coordinates']}}
    ],
    'responses': {
        200: {'description': 'Crop growth map URL'},
        400: {'description': 'Coordinates are required'}
    }
})
def crop_growth_map():
    data = request.json
    coordinates = data.get('coordinates')
    field_id = data.get('field_id', 'default')
    if not coordinates:
        return jsonify({'error': 'Coordinates are required'}), 400

    start_date, end_date = _default_dates()

    def image_func(geom):
        image = ee_service.get_sentinel2_image(geom, start_date, end_date)
        return ee_service.calculate_ndvi(image)

    vis = {"min": 0, "max": 1, "palette": ["white", "green"]}
    tile_url = _generate_map_url(field_id, 'crop_growth', coordinates, image_func, vis)
    return jsonify({
        "tile_url": tile_url,
        "description": "📈 NDVI map to monitor crop development over time."
    })


@field_bp.route('/disease-pest', methods=['POST'])
@require_api_key
@swag_from({
    'tags': ['Maps'],
    'parameters': [
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {'type': 'object', 'properties': {'coordinates': {'type': 'array'}, 'field_id': {'type': 'string'}}, 'required': ['coordinates']}}
    ],
    'responses': {
        200: {'description': 'Disease/pest NDVI anomaly map URL'},
        400: {'description': 'Coordinates are required'}
    }
})
def disease_pest_map():
    data = request.json
    coordinates = data.get('coordinates')
    field_id = data.get('field_id', 'default')
    if not coordinates:
        return jsonify({'error': 'Coordinates are required'}), 400

    start_date, end_date = _default_dates()

    def image_func(geom):
        image = ee_service.get_sentinel2_image(geom, start_date, end_date)
        ndvi = ee_service.calculate_ndvi(image)
        mean_ndvi = ndvi.reduceRegion(
            reducer=ee_service.Reducer.mean(),
            geometry=geom,
            scale=30
        ).get('NDVI')
        anomaly = ndvi.subtract(mean_ndvi).rename('NDVI_Anomaly')
        return anomaly

    vis = {"min": -0.2, "max": 0.2, "palette": ["red", "white", "green"]}
    tile_url = _generate_map_url(field_id, 'disease_pest', coordinates, image_func, vis)
    return jsonify({
        "tile_url": tile_url,
        "description": "🐛 NDVI anomaly map showing abnormal vegetation (potential disease/pests)."
    })