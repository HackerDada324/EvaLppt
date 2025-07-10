"""
Flask extensions initialization
"""
from flask_cors import CORS

def init_extensions(app):
    """Initialize Flask extensions"""
    
    # Enable CORS for all routes
    CORS(app, 
         origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React development server
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    return app
