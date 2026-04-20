"""
Violation routes — REST API endpoints for traffic violations.
Endpoints:
  POST /api/violation          → Create a new violation
  GET  /api/violations         → Fetch all violations (paginated)
  GET  /api/violations/filter  → Filter violations by criteria
  GET  /api/violations/<id>    → Get single violation detail
  GET  /api/stats              → Summary statistics
"""
from flask import Blueprint, request, jsonify
from controllers.violation_controller import ViolationController

violations_bp = Blueprint('violations', __name__)


@violations_bp.route('/api/violation', methods=['POST'])
def create_violation():
    """Store a new violation record."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    if not data.get('vehicle_number'):
        return jsonify({'error': 'vehicle_number is required'}), 400

    result = ViolationController.create_violation(data)
    return jsonify({'success': True, 'violation': result}), 201


@violations_bp.route('/api/violations', methods=['GET'])
def get_violations():
    """Fetch all violations with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    result = ViolationController.get_all_violations(page, per_page)
    return jsonify(result)


@violations_bp.route('/api/violations/filter', methods=['GET'])
def filter_violations():
    """Filter violations by date range, type, vehicle number."""
    filters = {
        'violation_type': request.args.get('violation_type'),
        'vehicle_number': request.args.get('vehicle_number'),
        'status': request.args.get('status'),
        'location': request.args.get('location'),
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'page': request.args.get('page', 1),
        'per_page': request.args.get('per_page', 20)
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    result = ViolationController.filter_violations(filters)
    return jsonify(result)


@violations_bp.route('/api/violations/<int:violation_id>', methods=['GET'])
def get_violation(violation_id):
    """Fetch a single violation by ID."""
    result = ViolationController.get_violation_by_id(violation_id)
    if result:
        return jsonify(result)
    return jsonify({'error': 'Violation not found'}), 404


@violations_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """Get summary statistics for the dashboard."""
    stats = ViolationController.get_stats()
    return jsonify(stats)
