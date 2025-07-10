"""
Auto PPT Evaluation System - Main Application Entry Point
"""
from app.app_factory import create_app

def main():
    """Main application entry point"""
    app = create_app()
    app.run(
        debug=app.config.get('DEBUG', False),
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000)
    )

if __name__ == '__main__':
    main()
