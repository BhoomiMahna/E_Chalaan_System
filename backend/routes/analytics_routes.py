from flask import Blueprint, jsonify
from services.report_service import ReportService
from services.hotspot_service import HotspotService
from services.prediction_service import PredictionService
from models.violation import Violation
from core.cache import cache
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)

report_service = ReportService()
hotspot_service = HotspotService()
prediction_service = PredictionService()

@analytics_bp.route('/api/analytics/report', methods=['GET'])
@cache(ttl_seconds=3600)  # Cache report for 1 hour
def get_report():
    """Get the daily automated report."""
    try:
        report = report_service.generate_daily_report()
        return jsonify(report)
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/api/analytics/hotspots', methods=['GET'])
@cache(ttl_seconds=3600)
def get_hotspots():
    """Get high-risk violation areas."""
    try:
        violations = [v.to_dict() for v in Violation.query.all()]
        hotspots = hotspot_service.identify_hotspots(violations)
        return jsonify({"hotspots": hotspots})
    except Exception as e:
        logger.error(f"Failed to identify hotspots: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/api/analytics/forecast', methods=['GET'])
@cache(ttl_seconds=86400) # Cache forecast for 24 hours
def get_forecast():
    """Get 7-day violation forecast."""
    try:
        violations = [v.to_dict() for v in Violation.query.all()]
        forecast = prediction_service.forecast_violations(violations)
        return jsonify({"forecast": forecast})
    except Exception as e:
        logger.error(f"Failed to generate forecast: {e}")
        return jsonify({"error": str(e)}), 500
