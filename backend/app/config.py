"""
Configuration settings for Auto PPT Evaluation Backend
"""
import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Model settings
    WHISPER_MODEL = os.environ.get('WHISPER_MODEL', 'base')
    FACIAL_EXPRESSION_MODEL = os.environ.get('FACIAL_EXPRESSION_MODEL', 'prithivMLmods/Facial-Emotion-Detection-SigLIP2')
    USE_GPU = os.environ.get('USE_GPU', 'True').lower() == 'true'
    
    # Analysis settings
    DEFAULT_TARGET_FPS = 5
    MAX_VIDEO_SIZE_MB = 100
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    
    # Processing settings
    MIN_DETECTION_CONFIDENCE = 0.7
    ANALYSIS_TIMEOUT_SECONDS = 300  # 5 minutes
    
    @classmethod
    def get_analyzer_config(cls) -> Dict[str, Any]:
        """Get configuration for analyzers"""
        return {
            'min_detection_confidence': cls.MIN_DETECTION_CONFIDENCE,
            'use_gpu': cls.USE_GPU,
            'whisper_model': cls.WHISPER_MODEL,
            'facial_expression_model': cls.FACIAL_EXPRESSION_MODEL,
            'gemini_api_key': cls.GEMINI_API_KEY
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, str]:
        """Validate configuration and return any warnings"""
        warnings = []
        
        if not cls.GEMINI_API_KEY:
            warnings.append("GEMINI_API_KEY not set - AI analysis features will be disabled")
        
        if cls.USE_GPU:
            try:
                import torch
                if not torch.cuda.is_available():
                    warnings.append("GPU requested but CUDA not available - using CPU")
            except ImportError:
                warnings.append("GPU requested but PyTorch not available - using CPU")
        
        return warnings

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-required'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get the current configuration based on environment"""
    env = config_name or os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
