import ee
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
import json
import os
import tempfile
import logging
from config import Config

logger = logging.getLogger(__name__)

class EarthEngineService:
    def __init__(self):
        self.initialized = False
        
    def initialize(self, project_id: Optional[str] = None):
        """Initialize Google Earth Engine with authentication."""
        try:
            service_account_key = os.getenv('GEE_SERVICE_ACCOUNT_KEY')

            if service_account_key:
                try:
                    key_data = json.loads(service_account_key)
                    service_account_email = key_data.get('client_email')

                    # Use a secure, cross-platform temporary file and remove it after initialization
                    tmp_file = None
                    try:
                        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                            tmp_file = f.name
                            json.dump(key_data, f)

                        credentials = ee.ServiceAccountCredentials(service_account_email, tmp_file)
                        ee.Initialize(credentials, project=project_id)

                        logger.info(f"Earth Engine initialized with service account: {service_account_email}")
                        self.initialized = True
                        return True
                    finally:
                        # Attempt to securely remove the temporary key file
                        if tmp_file and os.path.exists(tmp_file):
                            try:
                                os.remove(tmp_file)
                            except Exception:
                                logger.warning("Could not remove temporary GEE service account key file")
                except Exception as sa_error:
                    logger.warning(f"Service account authentication failed: {str(sa_error)}")
                    logger.info("Falling back to user authentication...")
            
            if project_id:
                ee.Initialize(project=project_id)
            else:
                ee.Initialize()
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Earth Engine initialization error: {str(e)}")
            return False
    
    def get_field_bounds(self, coordinates: List[List[float]]) -> ee.Geometry:
        """Convert coordinates to Earth Engine geometry."""
        return ee.Geometry.Polygon(coordinates)
    
    def calculate_ndvi(self, image: ee.Image) -> ee.Image:
        """Calculate Normalized Difference Vegetation Index."""
        nir = image.select('B8')
        red = image.select('B4')
        ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
        return ndvi
    
    def get_sentinel2_image(self, geometry: ee.Geometry, start_date: str, end_date: str) -> ee.Image:
        """Get cloud-filtered Sentinel-2 imagery for a specific time period."""
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                     .filterBounds(geometry)
                     .filterDate(start_date, end_date)
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                     .select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12']))
        
        return collection.median()
    
    def get_ndvi_statistics(self, ndvi_image: ee.Image, geometry: ee.Geometry) -> Dict:
        """Calculate NDVI statistics for a given area."""
        stats = ndvi_image.reduceRegion(
            reducer=ee.Reducer.mean().combine(
                ee.Reducer.minMax(), '', True
            ).combine(
                ee.Reducer.stdDev(), '', True
            ),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        )
        
        return stats.getInfo()
    
    def classify_productivity_zones(self, ndvi_image: ee.Image, geometry: ee.Geometry) -> Dict:
        """Classify field into high, medium, low productivity zones based on NDVI."""
        high_zone = ndvi_image.gte(Config.NDVI_THRESHOLDS['high'])
        medium_zone = ndvi_image.gte(Config.NDVI_THRESHOLDS['medium']).And(
            ndvi_image.lt(Config.NDVI_THRESHOLDS['high'])
        )
        low_zone = ndvi_image.lt(Config.NDVI_THRESHOLDS['medium'])
        try:
            total_pixels_obj = ndvi_image.reduceRegion(
                reducer=ee.Reducer.count(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            ).get('NDVI')

            high_pixels_obj = high_zone.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            ).get('NDVI')

            medium_pixels_obj = medium_zone.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            ).get('NDVI')

            low_pixels_obj = low_zone.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            ).get('NDVI')

            # Fetch server-side values and guard against divide-by-zero / missing data
            try:
                total_pixels = ee.Number(total_pixels_obj).getInfo() or 0
            except Exception:
                total_pixels = 0

            try:
                high_pixels = ee.Number(high_pixels_obj).getInfo() or 0
            except Exception:
                high_pixels = 0

            try:
                medium_pixels = ee.Number(medium_pixels_obj).getInfo() or 0
            except Exception:
                medium_pixels = 0

            try:
                low_pixels = ee.Number(low_pixels_obj).getInfo() or 0
            except Exception:
                low_pixels = 0

            if not total_pixels:
                logger.warning('No valid pixels returned for productivity classification; returning zeros')
                return {
                    'high_productivity_percent': 0.0,
                    'medium_productivity_percent': 0.0,
                    'low_productivity_percent': 0.0,
                    'note': 'no_valid_pixels'
                }

            return {
                'high_productivity_percent': (high_pixels / total_pixels) * 100,
                'medium_productivity_percent': (medium_pixels / total_pixels) * 100,
                'low_productivity_percent': (low_pixels / total_pixels) * 100
            }
        except Exception as e:
            logger.error(f'Error classifying productivity zones: {e}')
            return {
                'high_productivity_percent': 0.0,
                'medium_productivity_percent': 0.0,
                'low_productivity_percent': 0.0,
                'error': str(e)
            }
    
    def calculate_soil_moisture_index(self, image: ee.Image) -> ee.Image:
        """Calculate soil moisture index using SWIR bands."""
        swir1 = image.select('B11')
        swir2 = image.select('B12')
        nir = image.select('B8')
        
        ndmi = nir.subtract(swir1).divide(nir.add(swir1)).rename('NDMI')
        
        return ndmi
    
    def detect_water_stress(self, geometry: ee.Geometry, start_date: str, end_date: str) -> Dict:
        """Detect water stress areas using soil moisture indices."""
        image = self.get_sentinel2_image(geometry, start_date, end_date)
        ndmi = self.calculate_soil_moisture_index(image)
        
        stats = ndmi.reduceRegion(
            reducer=ee.Reducer.mean().combine(
                ee.Reducer.minMax(), '', True
            ),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).getInfo()
        
        water_stress = ndmi.lt(Config.WATER_STRESS_THRESHOLD)
        try:
            total_pixels_obj = ndmi.reduceRegion(
                reducer=ee.Reducer.count(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            ).get('NDMI')

            stress_pixels_obj = water_stress.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            ).get('NDMI')

            try:
                total_pixels = ee.Number(total_pixels_obj).getInfo() or 0
            except Exception:
                total_pixels = 0

            try:
                stress_pixels = ee.Number(stress_pixels_obj).getInfo() or 0
            except Exception:
                stress_pixels = 0

            if not total_pixels:
                logger.warning('No valid pixels returned for water stress detection; returning defaults')
                stress_percent = 0.0
            else:
                stress_percent = (stress_pixels / total_pixels) * 100

            return {
                'average_moisture_index': stats.get('NDMI_mean'),
                'min_moisture_index': stats.get('NDMI_min'),
                'max_moisture_index': stats.get('NDMI_max'),
                'water_stress_area_percent': stress_percent,
                'requires_irrigation': stress_percent > 30
            }
        except Exception as e:
            logger.error(f'Error detecting water stress: {e}')
            return {
                'average_moisture_index': stats.get('NDMI_mean'),
                'min_moisture_index': stats.get('NDMI_min'),
                'max_moisture_index': stats.get('NDMI_max'),
                'water_stress_area_percent': 0.0,
                'requires_irrigation': False,
                'error': str(e)
            }
    
    def get_time_series_ndvi(self, geometry: ee.Geometry, start_date: str, end_date: str, interval_days: int = 10) -> List[Dict]:
        """Get NDVI time series data for crop growth tracking."""
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                     .filterBounds(geometry)
                     .filterDate(start_date, end_date)
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
        
        def compute_ndvi(image):
            ndvi = self.calculate_ndvi(image)
            mean_ndvi = ndvi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            ).get('NDVI')
            
            return ee.Feature(None, {
                'date': image.date().format('YYYY-MM-dd'),
                'ndvi': mean_ndvi
            })
        
        time_series = collection.map(compute_ndvi).getInfo()
        
        results = []
        for feature in time_series['features']:
            props = feature['properties']
            if props.get('ndvi') is not None:
                results.append({
                    'date': props['date'],
                    'ndvi': props['ndvi']
                })
        
        return sorted(results, key=lambda x: x['date'])
    
    def detect_disease_risk(self, geometry: ee.Geometry, start_date: str, end_date: str) -> Dict:
        """Detect potential disease and pest risks using vegetation anomalies."""
        current_image = self.get_sentinel2_image(geometry, start_date, end_date)
        current_ndvi = self.calculate_ndvi(current_image)
        
        prev_start = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
        prev_end = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
        
        previous_image = self.get_sentinel2_image(geometry, prev_start, prev_end)
        previous_ndvi = self.calculate_ndvi(previous_image)
        
        ndvi_change = current_ndvi.subtract(previous_ndvi)
        
        stats = ndvi_change.reduceRegion(
            reducer=ee.Reducer.mean().combine(
                ee.Reducer.minMax(), '', True
            ).combine(
                ee.Reducer.stdDev(), '', True
            ),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).getInfo()
        
        anomaly_threshold = -Config.DISEASE_DETECTION_SENSITIVITY
        anomaly = ndvi_change.lt(anomaly_threshold)
        
        try:
            total_pixels_obj = ndvi_change.reduceRegion(
                reducer=ee.Reducer.count(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            ).get('NDVI')

            anomaly_pixels_obj = anomaly.reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=geometry,
                scale=10,
                maxPixels=1e9
            ).get('NDVI')

            try:
                total_pixels = ee.Number(total_pixels_obj).getInfo() or 0
            except Exception:
                total_pixels = 0

            try:
                anomaly_pixels = ee.Number(anomaly_pixels_obj).getInfo() or 0
            except Exception:
                anomaly_pixels = 0

            if not total_pixels:
                logger.warning('No valid pixels returned for disease detection; returning low risk')
                anomaly_percent = 0.0
            else:
                anomaly_percent = (anomaly_pixels / total_pixels) * 100

            risk_level = 'low'
            if anomaly_percent > 15:
                risk_level = 'high'
            elif anomaly_percent > 5:
                risk_level = 'medium'

            return {
                'ndvi_change_mean': stats.get('NDVI_mean'),
                'ndvi_change_min': stats.get('NDVI_min'),
                'ndvi_change_max': stats.get('NDVI_max'),
                'ndvi_change_stddev': stats.get('NDVI_stdDev'),
                'anomaly_area_percent': anomaly_percent,
                'risk_level': risk_level,
                'alert': risk_level in ['medium', 'high']
            }
        except Exception as e:
            logger.error(f'Error detecting disease risk: {e}')
            return {
                'ndvi_change_mean': stats.get('NDVI_mean'),
                'ndvi_change_min': stats.get('NDVI_min'),
                'ndvi_change_max': stats.get('NDVI_max'),
                'ndvi_change_stddev': stats.get('NDVI_stdDev'),
                'anomaly_area_percent': 0.0,
                'risk_level': 'low',
                'alert': False,
                'error': str(e)
            }
    
    def compare_historical_seasons(self, geometry: ee.Geometry, current_start: str, current_end: str, years_back: int = 1) -> Dict:
        """Compare current season with historical data."""
        current_image = self.get_sentinel2_image(geometry, current_start, current_end)
        current_ndvi = self.calculate_ndvi(current_image)
        
        current_stats = self.get_ndvi_statistics(current_ndvi, geometry)
        
        hist_start = (datetime.strptime(current_start, '%Y-%m-%d') - timedelta(days=365*years_back)).strftime('%Y-%m-%d')
        hist_end = (datetime.strptime(current_end, '%Y-%m-%d') - timedelta(days=365*years_back)).strftime('%Y-%m-%d')
        
        historical_image = self.get_sentinel2_image(geometry, hist_start, hist_end)
        historical_ndvi = self.calculate_ndvi(historical_image)
        
        historical_stats = self.get_ndvi_statistics(historical_ndvi, geometry)
        
        ndvi_diff = current_stats.get('NDVI_mean', 0) - historical_stats.get('NDVI_mean', 0)
        percent_change = (ndvi_diff / historical_stats.get('NDVI_mean', 1)) * 100 if historical_stats.get('NDVI_mean') else 0
        
        return {
            'current_season': {
                'start_date': current_start,
                'end_date': current_end,
                'mean_ndvi': current_stats.get('NDVI_mean'),
                'min_ndvi': current_stats.get('NDVI_min'),
                'max_ndvi': current_stats.get('NDVI_max')
            },
            'historical_season': {
                'start_date': hist_start,
                'end_date': hist_end,
                'mean_ndvi': historical_stats.get('NDVI_mean'),
                'min_ndvi': historical_stats.get('NDVI_min'),
                'max_ndvi': historical_stats.get('NDVI_max')
            },
            'comparison': {
                'ndvi_difference': ndvi_diff,
                'percent_change': percent_change,
                'performance': 'better' if ndvi_diff > 0 else 'worse' if ndvi_diff < 0 else 'similar'
            }
        }
