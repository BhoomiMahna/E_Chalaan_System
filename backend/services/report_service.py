from models.violation import Violation
from services.summary_service import SummaryService
from datetime import datetime, timedelta

class ReportService:
    def __init__(self):
        self.summary_service = SummaryService()

    def generate_daily_report(self):
        """Generate structured stats for the last 24 hours along with an AI summary."""
        # For demo purposes, we fetch all since dummy data spans broadly. 
        # In prod: filter(Violation.date_time >= datetime.now() - timedelta(days=1))
        violations = Violation.query.all()
        
        total = len(violations)
        helmet = sum(1 for v in violations if v.violation_type == 'no_helmet')
        red_light = sum(1 for v in violations if v.violation_type == 'red_light')
        total_fines = sum(v.fine_amount for v in violations)
        
        data_str = f"Total Violations: {total}, No Helmet: {helmet}, Red Light: {red_light}, Total Fine Amount: Rs {total_fines}"
        
        # Generate AI insight
        ai_summary = self.summary_service.generate_summary(data_str)
        
        return {
            "report_type": "Daily",
            "stats": {
                "total_violations": total,
                "no_helmet_count": helmet,
                "red_light_count": red_light,
                "total_fines": total_fines
            },
            "ai_insights": ai_summary
        }
