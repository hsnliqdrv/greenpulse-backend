import ee
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from config import Config

class EarthEngineService:
    def __init__(self):
        self.initialized = False
        
    def initialize(self, project_id: Optional[str] = None):
        """Initialize Google Earth Engine with authentication."""
        try:
            if project_id:
                ee.Initialize(project=project_id)
            else:
                ee.Initialize()
            self.initialized = True
            return True
        except Exception as e:
            print(f"Earth Engine initialization error: {str(e)}")
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
        
        total_pixels = ee.Number(ndvi_image.reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).get('NDVI'))
        
        high_pixels = high_zone.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).get('NDVI')
        
        medium_pixels = medium_zone.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).get('NDVI')
        
        low_pixels = low_zone.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).get('NDVI')
        
        result = {
            'high_productivity_percent': ee.Number(high_pixels).divide(total_pixels).multiply(100).getInfo(),
            'medium_productivity_percent': ee.Number(medium_pixels).divide(total_pixels).multiply(100).getInfo(),
            'low_productivity_percent': ee.Number(low_pixels).divide(total_pixels).multiply(100).getInfo()
        }
        
        return result
    
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
        
        total_pixels = ee.Number(ndmi.reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).get('NDMI'))
        
        stress_pixels = water_stress.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).get('NDMI')
        
        stress_percent = ee.Number(stress_pixels).divide(total_pixels).multiply(100).getInfo()
        
        return {
            'average_moisture_index': stats.get('NDMI_mean'),
            'min_moisture_index': stats.get('NDMI_min'),
            'max_moisture_index': stats.get('NDMI_max'),
            'water_stress_area_percent': stress_percent,
            'requires_irrigation': stress_percent > 30
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
        
        total_pixels = ee.Number(ndvi_change.reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).get('NDVI'))
        
        anomaly_pixels = anomaly.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9
        ).get('NDVI')
        
        anomaly_percent = ee.Number(anomaly_pixels).divide(total_pixels).multiply(100).getInfo()
        
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
