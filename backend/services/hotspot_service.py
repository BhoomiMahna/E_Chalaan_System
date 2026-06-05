from collections import Counter
import logging

logger = logging.getLogger(__name__)

class HotspotService:
    def identify_hotspots(self, violations_data):
        """Identify high-risk areas based on historical violation counts."""
        if not violations_data:
            return []
        
        location_counts = Counter(v.get('location', 'Unknown') for v in violations_data)
        total = len(violations_data)
        areas = []
        for loc, count in location_counts.most_common(10):
            risk = 'high' if count / total > 0.15 else 'medium' if count / total > 0.08 else 'low'
            areas.append({
                'location': loc,
                'violation_count': count,
                'percentage': round(count / total * 100, 1),
                'risk_level': risk
            })
        return areas
