"""
AI routes — REST API endpoints for the AI assistant.
Endpoints:
  POST /api/ai/query          → Natural language database query
  POST /api/ai/explain/<id>   → Generate violation explanation
  GET  /api/ai/predict        → Get predictive analytics
"""
from flask import Blueprint, request, jsonify
from controllers.ai_controller import AIController

ai_bp = Blueprint('ai', __name__)
ai_controller = AIController()


@ai_bp.route('/api/ai/query', methods=['POST'])
def ai_query():
    """Process a natural language query and return database results."""
    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({'error': 'Query string required'}), 400

    result = ai_controller.process_query(data['query'])
    return jsonify(result)


@ai_bp.route('/api/ai/explain/<int:violation_id>', methods=['POST'])
def ai_explain(violation_id):
    """Generate a human-readable explanation for a violation."""
    result = ai_controller.generate_explanation(violation_id)
    if result.get('success'):
        return jsonify(result)
    return jsonify(result), 404


@ai_bp.route('/api/ai/predict', methods=['GET'])
def ai_predict():
    """Get predictive analytics — high-risk areas and peak times."""
    result = ai_controller.get_predictions()
    return jsonify(result)
