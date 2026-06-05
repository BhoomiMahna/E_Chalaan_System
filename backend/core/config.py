import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database - defaults to SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///echallan.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret Key (for sessions, etc.)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # LLM configuration (Local RAG)
    LOCAL_LLM_MODEL = os.getenv('LOCAL_LLM_MODEL', 'llama3')
    VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', './chroma_db')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)
    
    # Caching
    CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', 60))
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100/hour')

    # CORS Origins
    cors_origins_env = os.getenv('CORS_ORIGINS', 'http://localhost:5173')
    CORS_ORIGINS = [origin.strip() for origin in cors_origins_env.split(',') if origin.strip()]

    # CV Module settings
    YOLO_MODEL_PATH = os.getenv('YOLO_MODEL_PATH', 'yolov8n.pt')
    YOLO_CONFIDENCE_THRESHOLD = float(os.getenv('YOLO_CONFIDENCE', '0.5'))
    FRAME_SKIP = int(os.getenv('FRAME_SKIP', '5'))  # Process every Nth frame
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
    VIOLATION_IMAGES_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'violation_images')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
