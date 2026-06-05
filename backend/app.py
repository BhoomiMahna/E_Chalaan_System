"""
Traffic E-Challan System — Flask Application Factory.
Main entry point for the backend API server.
Run: python app.py
"""
import os
import sys
import logging

# Add backend dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
from models import db
from core.startup_validator import validate_environment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Application factory — creates and configures the Flask app."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:5173']))

    # Initialize Rate Limiter
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[app.config.get('RATELIMIT_DEFAULT', '100/hour')],
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')  # fallback to memory if redis fails
    )
    # Expose limiter to be used in other modules
    app.limiter = limiter

    # Create upload directories
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs(app.config.get('VIOLATION_IMAGES_FOLDER', 'violation_images'), exist_ok=True)

    # Register blueprints
    from routes.violations import violations_bp
    from routes.ai_routes import ai_bp
    from routes.cv_routes import cv_bp
    from routes.analytics_routes import analytics_bp

    app.register_blueprint(violations_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(cv_bp)
    app.register_blueprint(analytics_bp)

    # Validate Environment Variables on Startup
    with app.app_context():
        validate_environment()
        logger.info("Environment variables verified.")

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Traffic E-Challan System',
            'version': '1.0.0'
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    logger.info(f"App created with config: {config_name}")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
