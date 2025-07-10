"""
API Blueprint registration
"""
from .v1 import api_v1

def register_blueprints(app):
    """Register all API blueprints"""
    
    # Register API v1
    app.register_blueprint(api_v1, url_prefix='/api')
    
    return app
