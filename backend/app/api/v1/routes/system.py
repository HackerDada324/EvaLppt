"""
System information and testing routes
"""
from flask import jsonify, current_app
from datetime import datetime

def register_routes(bp):
    """Register system routes"""
    
    @bp.route('/test', methods=['GET'])
    def test_api():
        """System test endpoint with analyzer status"""
        analyzer_service = current_app.analyzer_service
        
        # Check which analyzers are available
        analyzer_status = analyzer_service.get_analyzer_status()
        dependency_status = analyzer_service.get_dependency_status()
        
        return jsonify({
            'status': 'success',
            'message': 'Auto PPT Evaluation API is working correctly',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'features': {
                'video_analysis': True,
                'audio_analysis': dependency_status.get('audio_analysis_available', False),
                'ai_content_analysis': analyzer_service.is_analyzer_available('content'),
                'comprehensive_evaluation': analyzer_service.is_analyzer_available('evaluator'),
                'real_time_progress': True
            },
            'analyzers_available': analyzer_status,
            'dependencies': dependency_status,
            'analyzer_count': {
                'available': analyzer_service.get_available_analyzer_count(),
                'total': analyzer_service.get_total_analyzer_count()
            },
            'api_endpoints': [
                'POST /api/analyze-video - Upload and analyze presentation video',
                'GET /api/analysis/{id}/status - Check analysis progress',
                'GET /api/analysis/{id}/results - Get full analysis results',
                'GET /api/analysis/{id}/score - Get presentation score and feedback',
                'GET /api/analysis/{id}/detailed-feedback - Get detailed category feedback',
                'GET /api/summary - Get analysis summary statistics',
                'GET /api/health - Health check',
                'GET /api/test - This endpoint',
                'GET /api/info - System information'
            ]
        })
    
    @bp.route('/info', methods=['GET'])
    def system_info():
        """Get detailed system information"""
        analyzer_service = current_app.analyzer_service
        
        return jsonify({
            'service': 'Auto PPT Evaluation System',
            'version': '2.0.0',
            'environment': current_app.config.get('ENV', 'unknown'),
            'debug_mode': current_app.config.get('DEBUG', False),
            'analyzer_counts': {
                'total_analyzers': analyzer_service.get_total_analyzer_count(),
                'available_analyzers': analyzer_service.get_available_analyzer_count()
            },
            'capabilities': {
                'supported_formats': ['mp4', 'avi', 'mov', 'mkv', 'wmv'],
                'max_file_size_mb': current_app.config.get('MAX_VIDEO_SIZE_MB', 100),
                'supported_analysis_types': [
                    'body_language_analysis',
                    'facial_expression_analysis', 
                    'vocal_delivery_analysis',
                    'content_quality_analysis',
                    'comprehensive_scoring'
                ]
            },
            'api_version': 'v1',
            'timestamp': datetime.now().isoformat()
        })
