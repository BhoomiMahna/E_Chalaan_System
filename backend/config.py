"""
Configuration management for the Traffic E-Challan System.
Supports dev (SQLite) and production (PostgreSQL) environments.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    # Database - defaults to SQLite (zero setup)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///echallan.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')

    # Fine amounts (in INR)
    FINE_AMOUNTS = {
        'no_helmet': 1000,
        'red_light': 5000
    }

    # CV Module settings
    YOLO_MODEL_PATH = os.getenv('YOLO_MODEL_PATH', 'yolov8n.pt')
    YOLO_CONFIDENCE_THRESHOLD = float(os.getenv('YOLO_CONFIDENCE', '0.5'))
    FRAME_SKIP = int(os.getenv('FRAME_SKIP', '5'))  # Process every Nth frame
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    VIOLATION_IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'violation_images')

    # Locations for simulation/demo
    LOCATIONS = [
        'MG Road, Sector 17',
        'NH-44, Panipat Bypass',
        'GT Road, Ludhiana',
        'Rajpura Chowk, Patiala',
        'Bus Stand, Jalandhar',
        'Mall Road, Shimla',
        'Ferozepur Road, Ludhiana',
        'Chandigarh-Ambala Highway',
        'Civil Lines, Amritsar',
        'Model Town, Karnal'
    ]


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
