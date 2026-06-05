from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PredictionService:
    def forecast_violations(self, data):
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
