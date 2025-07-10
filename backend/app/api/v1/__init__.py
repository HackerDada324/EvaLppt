"""
API v1 Blueprint
"""
from flask import Blueprint
from .routes import analysis, health, system

# Create API v1 blueprint
api_v1 = Blueprint('api_v1', __name__)

# Register route modules
analysis.register_routes(api_v1)
health.register_routes(api_v1)
system.register_routes(api_v1)
