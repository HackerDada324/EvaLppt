"""
Health and system status routes
"""
from flask import jsonify
from datetime import datetime

def register_routes(bp):
    """Register health routes"""
    
    @bp.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Auto PPT Evaluation API',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat()
        })
    
    @bp.route('/ping', methods=['GET'])
    def ping():
        """Simple ping endpoint"""
        return jsonify({
            'message': 'pong',
            'timestamp': datetime.now().isoformat()
        })
