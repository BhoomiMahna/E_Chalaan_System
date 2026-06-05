from celery_app import celery_app
from services.report_service import ReportService
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name='generate_daily_report_async')
def generate_daily_report_async():
    """Background task to generate and cache the daily report."""
    try:
        report_service = ReportService()
        report = report_service.generate_daily_report()
        logger.info("Daily report generated asynchronously.")
        return report
    except Exception as e:
        logger.error(f"Failed to generate async report: {e}")
        return str(e)
