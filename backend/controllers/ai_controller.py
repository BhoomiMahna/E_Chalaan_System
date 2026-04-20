"""
AI Controller — Business logic for the AI assistant features.
Delegates to query_agent, explanation_agent, and prediction_model.
"""
from ai_module.query_agent import QueryAgent
from ai_module.explanation_agent import ExplanationAgent
from ai_module.prediction_model import PredictionModel
from models.violation import Violation


class AIController:
    """Handles AI assistant business logic."""

    def __init__(self, app=None):
        self.query_agent = QueryAgent()
        self.explanation_agent = ExplanationAgent()
        self.prediction_model = PredictionModel()

    def process_query(self, natural_language_query):
        """Convert natural language to SQL, execute, and return results."""
        try:
            result = self.query_agent.process(natural_language_query)
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_explanation(self, violation_id):
        """Generate a human-readable explanation for a violation."""
        violation = Violation.query.get(violation_id)
        if not violation:
            return {'success': False, 'error': 'Violation not found'}

        try:
            explanation = self.explanation_agent.explain(violation.to_dict())
            return {'success': True, 'explanation': explanation}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_predictions(self):
        """Get predictive analytics results."""
        try:
            violations = Violation.query.all()
            data = [v.to_dict() for v in violations]
            predictions = self.prediction_model.predict(data)
            return {'success': True, 'predictions': predictions}
        except Exception as e:
            return {'success': False, 'error': str(e)}
