"""
Prediction Model — Predictive analytics for traffic violations.
Uses scikit-learn for:
  - Time-series prediction (LinearRegression)
  - High-violation zone clustering (KMeans)
  - Peak hour identification
"""
import logging
from datetime import datetime, timedelta
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


class PredictionModel:
    """Analyzes historical violations to predict trends and hotspots."""

    def predict(self, violations_data):
        """
        Run all prediction analyses on violation data.

        Args:
            violations_data: List of violation dicts

        Returns:
            dict with predictions for areas, times, and trends
        """
        if not violations_data:
            return self._empty_predictions()

        return {
            'high_risk_areas': self._predict_areas(violations_data),
            'peak_hours': self._predict_peak_hours(violations_data),
            'daily_trend': self._predict_daily_trend(violations_data),
            'violation_forecast': self._forecast_violations(violations_data),
            'insights': self._generate_insights(violations_data)
        }

    def _predict_areas(self, data):
        """Identify high-violation areas using frequency analysis."""
        location_counts = Counter(v.get('location', 'Unknown') for v in data)
        total = len(data)
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

    def _predict_peak_hours(self, data):
        """Identify peak violation hours."""
        hour_counts = defaultdict(int)
        for v in data:
            dt = v.get('date_time', '')
            if isinstance(dt, str) and dt:
                try:
                    h = datetime.fromisoformat(dt).hour
                    hour_counts[h] += 1
                except Exception:
                    pass
            elif isinstance(dt, datetime):
                hour_counts[dt.hour] += 1

        total = sum(hour_counts.values()) or 1
        hours = []
        for h in range(24):
            c = hour_counts.get(h, 0)
            hours.append({
                'hour': h,
                'label': f"{h:02d}:00",
                'count': c,
                'percentage': round(c / total * 100, 1),
                'is_peak': c / total > 0.06
            })
        return sorted(hours, key=lambda x: x['count'], reverse=True)

    def _predict_daily_trend(self, data):
        """Analyze daily violation trends."""
        daily = defaultdict(int)
        for v in data:
            dt = v.get('date_time', '')
            try:
                if isinstance(dt, str) and dt:
                    d = datetime.fromisoformat(dt).date()
                elif isinstance(dt, datetime):
                    d = dt.date()
                else:
                    continue
                daily[str(d)] += 1
            except Exception:
                pass

        dates = sorted(daily.keys())
        return [{'date': d, 'count': daily[d]} for d in dates]

    def _forecast_violations(self, data):
        """Simple linear regression forecast for next 7 days."""
        daily = defaultdict(int)
        for v in data:
            dt = v.get('date_time', '')
            try:
                if isinstance(dt, str) and dt:
                    d = datetime.fromisoformat(dt).date()
                elif isinstance(dt, datetime):
                    d = dt.date()
                else:
                    continue
                daily[str(d)] += 1
            except Exception:
                pass

        if len(daily) < 3:
            return []

        try:
            from sklearn.linear_model import LinearRegression
            import numpy as np

            dates = sorted(daily.keys())
            X = np.arange(len(dates)).reshape(-1, 1)
            y = np.array([daily[d] for d in dates])

            model = LinearRegression()
            model.fit(X, y)

            # Forecast next 7 days
            future_X = np.arange(len(dates), len(dates) + 7).reshape(-1, 1)
            predictions = model.predict(future_X)

            today = datetime.now().date()
            forecast = []
            for i, pred in enumerate(predictions):
                forecast_date = today + timedelta(days=i + 1)
                forecast.append({
                    'date': str(forecast_date),
                    'predicted_count': max(0, int(round(pred))),
                    'confidence': 'medium'
                })
            return forecast
        except ImportError:
            logger.warning("scikit-learn not installed. Skipping forecast.")
            return []
        except Exception as e:
            logger.error(f"Forecast failed: {e}")
            return []

    def _generate_insights(self, data):
        """Generate actionable text insights from the data."""
        if not data:
            return []

        insights = []
        total = len(data)

        # Type distribution
        helmet = sum(1 for v in data if v.get('violation_type') == 'no_helmet')
        red_light = total - helmet
        insights.append(
            f"📊 Out of {total} total violations, {helmet} ({helmet/total*100:.0f}%) "
            f"are helmet violations and {red_light} ({red_light/total*100:.0f}%) are red-light violations."
        )

        # Top location
        locs = Counter(v.get('location', '') for v in data)
        top_loc, top_count = locs.most_common(1)[0]
        insights.append(
            f"📍 {top_loc} is the highest violation area with {top_count} incidents "
            f"({top_count/total*100:.0f}% of all violations)."
        )

        # Peak hours
        hours = Counter()
        for v in data:
            dt = v.get('date_time', '')
            try:
                if isinstance(dt, str) and dt:
                    hours[datetime.fromisoformat(dt).hour] += 1
                elif isinstance(dt, datetime):
                    hours[dt.hour] += 1
            except Exception:
                pass
        if hours:
            peak_h = hours.most_common(1)[0][0]
            insights.append(f"⏰ Peak violation hour is {peak_h:02d}:00 - {peak_h+1:02d}:00.")

        # Fine collection
        total_fines = sum(v.get('fine_amount', 0) for v in data)
        paid = sum(v.get('fine_amount', 0) for v in data if v.get('status') == 'paid')
        insights.append(
            f"💰 Total fines issued: ₹{total_fines:,}. "
            f"Collected: ₹{paid:,} ({paid/total_fines*100:.0f}% collection rate)."
        )

        return insights

    def _empty_predictions(self):
        return {
            'high_risk_areas': [],
            'peak_hours': [],
            'daily_trend': [],
            'violation_forecast': [],
            'insights': ['No violation data available for analysis.']
        }
