from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from video_analysis.motion_analyzer.body_motion import BodyMotionAnalyzer
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize analyzers
body_analyzer = BodyMotionAnalyzer()

@app.route('/api/analyze-body-motion', methods=['POST'])
def analyze_body_motion():
    """Endpoint to analyze body motion in a video file"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    
    # Save uploaded file to a temporary location
    temp_dir = tempfile.gettempdir()
    video_path = os.path.join(temp_dir, video_file.filename)
    video_file.save(video_path)
    
    try:
        # Process the video with your analyzer
        target_fps = request.form.get('target_fps')
        if target_fps:
            target_fps = float(target_fps)
        else:
            target_fps = 5  # Default value
            
        # Run analysis
        stats = body_analyzer.process_video(
            video_path=video_path,
            target_fps=target_fps,
            show_progress=True
        )
        
        # Convert to JSON-serializable format
        if stats:
            response = {
                'mean_angle': stats.mean_angle,
                'median_angle': stats.median_angle,
                'std_dev_angle': stats.std_dev_angle,
                'min_angle': stats.min_angle,
                'max_angle': stats.max_angle,
                'dominant_direction': stats.dominant_direction,
                'direction_percentages': stats.direction_percentages,
                'stability_score': stats.stability_score,
                'frames_analyzed': stats.frames_analyzed,
                'frames_with_detection': stats.frames_with_detection,
                'detection_rate': stats.detection_rate,
                'duration_seconds': stats.duration_seconds
            }
            return jsonify(response)
        else:
            return jsonify({'error': 'No valid detection in video frames'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temporary file
        if os.path.exists(video_path):
            os.remove(video_path)

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Return a mock summary for testing frontend integration"""
    # In a real app, this would fetch data from a database
    return jsonify({
        'body_motion': {
            'mean_angle': 4.23,
            'stability_score': 2.15,
            'dominant_direction': 'right'
        },
        'head_motion': {
            'mean_angle': 3.67,
            'stability_score': 1.92,
            'dominant_direction': 'center'
        },
        'hand_motion': {
            'activity_level': 'moderate',
            'gesture_count': 15
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)