import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGODB_SETTINGS = {
        'host': os.getenv('DATABASE_URL', 'mongodb://localhost:27017/mywelthai'),
        'connect': False,
    }
    JSON_SORT_KEYS = False

    # Groq API Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MONGODB_SETTINGS = {
        'host': os.getenv('DATABASE_URL', 'mongodb://localhost:27017/mywelthai_test'),
        'connect': False,
    }


config_name = os.getenv('FLASK_ENV', 'development')
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
config = config.get(config_name, DevelopmentConfig)
