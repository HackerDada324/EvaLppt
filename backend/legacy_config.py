"""
Configuration for legacy app.py
"""
import os

class Config:
    """Configuration class for legacy app"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    
    @staticmethod
    def get_analyzer_config():
        """Get analyzer configuration"""
        return {
            'min_detection_confidence': float(os.environ.get('MIN_DETECTION_CONFIDENCE', '0.5')),
            'facial_expression_model': os.environ.get('FACIAL_EXPRESSION_MODEL', 'fer2013_mini_XCEPTION.102-0.66.hdf5'),
            'whisper_model': os.environ.get('WHISPER_MODEL', 'base'),
            'gemini_api_key': os.environ.get('GEMINI_API_KEY'),
            'use_gpu': os.environ.get('USE_GPU', 'False').lower() == 'true'
        }
    
    @staticmethod
    def validate_config():
        """Validate configuration and return warnings"""
        warnings = []
        
        if not os.environ.get('GEMINI_API_KEY'):
            warnings.append("GEMINI_API_KEY not set - AI analysis features will be disabled")
        
        return warnings

def get_config():
    """Get configuration class"""
    return Config
