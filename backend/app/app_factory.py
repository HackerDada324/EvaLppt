"""
Application Factory Pattern for Auto PPT Evaluation System
"""
from flask import Flask
from datetime import datetime
import os

from .config import get_config
from .extensions import init_extensions
from .api import register_blueprints
from .services.analyzer_service import AnalyzerService


def create_app(config_name=None):
    """
    Application factory pattern for creating Flask app instances
    
    Args:
        config_name: Configuration environment name ('development', 'production', etc.)
        
    Returns:
        Flask: Configured Flask application instance
    """
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize extensions (CORS, etc.)
    init_extensions(app)
    
    # Initialize analyzer service
    analyzer_service = AnalyzerService()
    analyzer_service.initialize_all_analyzers()
    
    # Store analyzer service in app context for dependency injection
    app.analyzer_service = analyzer_service
    
    # Register API blueprints
    register_blueprints(app)
    
    # Add startup information (called once during app creation)
    print(f"🚀 Auto PPT Evaluation System v2.0.0")
    print(f"📅 Started at: {datetime.now().isoformat()}")
    print(f"🔧 Environment: {app.config.get('ENV', 'unknown')}")
    print(f"🌐 Server: http://{app.config.get('HOST', 'localhost')}:{app.config.get('PORT', 5000)}")
    print("✅ Application ready!")
    
    # Add error handlers
    register_error_handlers(app)
    
    return app


def register_error_handlers(app):
    """Register application-wide error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return {'error': 'File too large'}, 413
