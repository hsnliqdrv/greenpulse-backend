import json
import csv
from io import StringIO
from typing import Dict, List
from datetime import datetime

class ReportService:
    @staticmethod
    def generate_json_report(field_data: Dict) -> str:
        """Generate JSON report of field analysis."""
        report = {
            'report_generated': datetime.now().isoformat(),
            'field_analysis': field_data
        }
        return json.dumps(report, indent=2)
    
    @staticmethod
    def generate_csv_report(field_data: Dict) -> str:
        """Generate CSV report of field analysis."""
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['GreenPulse Field Analysis Report'])
        writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        if 'yield_prediction' in field_data:
            writer.writerow(['Yield Prediction'])
            yp = field_data['yield_prediction']
            writer.writerow(['High Productivity %', yp.get('high_productivity_percent', 0)])
            writer.writerow(['Medium Productivity %', yp.get('medium_productivity_percent', 0)])
            writer.writerow(['Low Productivity %', yp.get('low_productivity_percent', 0)])
            if 'ndvi_stats' in yp:
                writer.writerow(['Average NDVI', yp['ndvi_stats'].get('NDVI_mean', 0)])
            writer.writerow([])
        
        if 'water_stress' in field_data:
            writer.writerow(['Water Stress Analysis'])
            ws = field_data['water_stress']
            writer.writerow(['Water Stress Area %', ws.get('water_stress_area_percent', 0)])
            writer.writerow(['Average Moisture Index', ws.get('average_moisture_index', 0)])
            writer.writerow(['Irrigation Required', 'Yes' if ws.get('requires_irrigation') else 'No'])
            writer.writerow([])
        
        if 'disease_risk' in field_data:
            writer.writerow(['Disease & Pest Risk'])
            dr = field_data['disease_risk']
            writer.writerow(['Risk Level', dr.get('risk_level', 'unknown')])
            writer.writerow(['Anomaly Area %', dr.get('anomaly_area_percent', 0)])
            writer.writerow(['Alert Status', 'ACTIVE' if dr.get('alert') else 'None'])
            writer.writerow([])
        
        if 'historical_comparison' in field_data:
            writer.writerow(['Historical Comparison'])
            hc = field_data['historical_comparison']
            comp = hc.get('comparison', {})
            writer.writerow(['Performance', comp.get('performance', 'unknown')])
            writer.writerow(['Percent Change', comp.get('percent_change', 0)])
            writer.writerow([])
        
        if 'crop_growth' in field_data:
            writer.writerow(['Crop Growth Time Series'])
            writer.writerow(['Date', 'NDVI'])
            cg = field_data['crop_growth']
            for data_point in cg.get('time_series', []):
                writer.writerow([data_point.get('date'), data_point.get('ndvi')])
            writer.writerow([])
        
        return output.getvalue()
    
    @staticmethod
    def generate_summary_statistics(field_data: Dict) -> Dict:
        """Generate summary statistics from all field analyses."""
        summary = {
            'overall_health_score': 0,
            'critical_alerts': [],
            'recommendations_count': 0
        }
        
        alerts = []
        health_factors = []
        
        if 'yield_prediction' in field_data:
            yp = field_data['yield_prediction']
            high_percent = yp.get('high_productivity_percent', 0)
            health_factors.append(high_percent)
            
            if yp.get('low_productivity_percent', 0) > 40:
                alerts.append("High percentage of low productivity areas detected")
        
        if 'water_stress' in field_data:
            ws = field_data['water_stress']
            if ws.get('requires_irrigation'):
                alerts.append("Irrigation required - significant water stress detected")
            
            moisture_score = (ws.get('average_moisture_index', 0) + 1) * 50
            health_factors.append(moisture_score)
        
        if 'disease_risk' in field_data:
            dr = field_data['disease_risk']
            if dr.get('alert'):
                alerts.append(f"Disease/pest risk alert: {dr.get('risk_level')} level")
            
            risk_penalty = {'high': 30, 'medium': 15, 'low': 5}
            health_factors.append(100 - risk_penalty.get(dr.get('risk_level', 'low'), 5))
        
        if health_factors:
            summary['overall_health_score'] = sum(health_factors) / len(health_factors)
        
        summary['critical_alerts'] = alerts
        summary['recommendations_count'] = len(alerts)
        
        return summary
