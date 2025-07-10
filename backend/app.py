from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import uuid
import time
from datetime import datetime
import traceback
from legacy_config import get_config

# Load configuration
Config = get_config()

# Try to import optional dependencies
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠ Warning: Whisper not available. Audio transcription will be disabled.")

try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("⚠ Warning: MoviePy not available. Audio extraction will be disabled.")

# Import all analysis modules
try:
    from video_analysis.motion_analyzer.body_rotation import BodyRotationAnalyzer
    from video_analysis.motion_analyzer.head_motion import HeadMotionAnalyzer
    from video_analysis.motion_analyzer.head_rotation import HeadRotationAnalyzer
    from video_analysis.motion_analyzer.head_pitch import HeadPitchAnalyzer
    from video_analysis.motion_analyzer.hand_motion import HandMotionAnalyzer
    from video_analysis.motion_analyzer.gaze_motion import GazeMotionAnalyzer
    from video_analysis.motion_analyzer.body_tilt import BodyTiltAnalyzer
    VIDEO_ANALYSIS_AVAILABLE = True
except ImportError as e:
    VIDEO_ANALYSIS_AVAILABLE = False
    print(f"⚠ Warning: Video analysis modules not available: {e}")

try:
    from video_analysis.expression_analyzer.expression import FacialExpressionAnalyzer
    EXPRESSION_ANALYSIS_AVAILABLE = True
except ImportError as e:
    EXPRESSION_ANALYSIS_AVAILABLE = False
    print(f"⚠ Warning: Expression analysis not available: {e}")

try:
    from audio_analysis.content_analyzer.content import ContentAnalyzer
    from audio_analysis.disfluency_analyzer.disfluency import DisfluencyTagger
    AUDIO_ANALYSIS_AVAILABLE = True
except ImportError as e:
    AUDIO_ANALYSIS_AVAILABLE = False
    print(f"⚠ Warning: Audio analysis modules not available: {e}")

try:
    from evaluation.evaluator import PresentationEvaluator
    EVALUATION_AVAILABLE = True
except ImportError as e:
    EVALUATION_AVAILABLE = False
    print(f"⚠ Warning: Evaluation module not available: {e}")

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for all routes

# Initialize analyzers conditionally
analyzers = {}

def initialize_analyzers():
    """Initialize all available analyzers"""
    global analyzers
    
    config_dict = Config.get_analyzer_config()
    
    if VIDEO_ANALYSIS_AVAILABLE:
        try:
            analyzers['body_rotation'] = BodyRotationAnalyzer(
                min_detection_confidence=config_dict['min_detection_confidence']
            )
            analyzers['head_motion'] = HeadMotionAnalyzer(
                min_detection_confidence=config_dict['min_detection_confidence']
            )
            analyzers['head_rotation'] = HeadRotationAnalyzer(
                min_detection_confidence=config_dict['min_detection_confidence']
            )
            analyzers['head_pitch'] = HeadPitchAnalyzer(
                min_detection_confidence=config_dict['min_detection_confidence']
            )
            analyzers['hand_motion'] = HandMotionAnalyzer(
                min_detection_confidence=config_dict['min_detection_confidence']
            )
            analyzers['gaze_motion'] = GazeMotionAnalyzer(
                min_detection_confidence=config_dict['min_detection_confidence']
            )
            analyzers['body_tilt'] = BodyTiltAnalyzer(
                min_detection_confidence=config_dict['min_detection_confidence']
            )
            print("✓ Video motion analyzers initialized successfully")
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize video analyzers: {e}")
    
    if EXPRESSION_ANALYSIS_AVAILABLE:
        try:
            analyzers['expression'] = FacialExpressionAnalyzer(
                model_name=config_dict['facial_expression_model'],
                use_gpu=config_dict['use_gpu']
            )
            print("✓ Expression analyzer initialized successfully")
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize expression analyzer: {e}")

def initialize_ai_analyzers():
    """Initialize AI-based analyzers with API keys from environment variables"""
    global analyzers
    
    if not AUDIO_ANALYSIS_AVAILABLE:
        print("⚠ Warning: Audio analysis modules not available")
        return
    
    config_dict = Config.get_analyzer_config()
    gemini_api_key = config_dict['gemini_api_key']
    
    if gemini_api_key:
        try:
            analyzers['content'] = ContentAnalyzer(api_key=gemini_api_key)
            analyzers['disfluency'] = DisfluencyTagger(api_key=gemini_api_key)
            print("✓ AI analyzers initialized successfully")
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize AI analyzers: {e}")
    else:
        print("⚠ Warning: GEMINI_API_KEY not found. Content and disfluency analysis will be disabled.")
    
    # Initialize Whisper for transcription
    if WHISPER_AVAILABLE:
        try:
            analyzers['whisper'] = whisper.load_model(config_dict['whisper_model'])
            print("✓ Whisper model loaded successfully")
        except Exception as e:
            print(f"⚠ Warning: Failed to load Whisper model: {e}")

    # Initialize Presentation Evaluator
    if EVALUATION_AVAILABLE:
        try:
            analyzers['evaluator'] = PresentationEvaluator()
            print("✓ Presentation evaluator initialized successfully")
        except Exception as e:
            print(f"⚠ Warning: Failed to initialize presentation evaluator: {e}")

    # Print configuration warnings
    warnings = Config.validate_config()
    for warning in warnings:
        print(f"⚠ Warning: {warning}")

def extract_audio_from_video(video_path, audio_path):
    """Extract audio from video file"""
    if not MOVIEPY_AVAILABLE:
        return False
    
    try:
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path, verbose=False, logger=None)
        video.close()
        audio.close()
        return True
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return False

def transcribe_audio(audio_path):
    """Transcribe audio file using Whisper"""
    whisper_model = analyzers.get('whisper')
    if whisper_model is None:
        return None
    
    try:
        result = whisper_model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

# In-memory storage for analyses (in production, use a database)
analyses = {}

# Initialize analyzers on startup
print("🚀 Initializing analyzers...")
initialize_analyzers()
initialize_ai_analyzers()
print("✅ Server initialization complete!")

@app.route('/api/analyze-video', methods=['POST'])
def analyze_video():
    """Comprehensive video analysis endpoint"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    
    # Save uploaded file to temporary location
    temp_dir = tempfile.gettempdir()
    video_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{video_file.filename}")
    audio_path = os.path.join(temp_dir, f"{uuid.uuid4()}_audio.wav")
    video_file.save(video_path)
    
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Store initial analysis info
        analyses[analysis_id] = {
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'filename': video_file.filename,
            'results': None,
            'progress': 0
        }
        
        # Get analysis parameters
        target_fps = request.form.get('target_fps', 5, type=float)
        
        results = {}
        total_steps = 11  # Updated to include evaluation step
        current_step = 0
        transcript = None  # Store transcript for evaluation
        
        # Step 1: Body Rotation Analysis
        try:
            analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
            if 'body_rotation' in analyzers:
                body_rotation_stats = analyzers['body_rotation'].process_video(video_path, target_fps=target_fps)
                results['body_rotation'] = {
                    'mean_angle': body_rotation_stats.mean_rotation_angle,
                    'median_angle': body_rotation_stats.median_rotation_angle,
                    'std_dev_angle': body_rotation_stats.std_dev_rotation_angle,
                    'min_angle': body_rotation_stats.min_rotation_angle,
                    'max_angle': body_rotation_stats.max_rotation_angle,
                    'dominant_direction': body_rotation_stats.dominant_rotation_direction,
                    'direction_percentages': body_rotation_stats.rotation_direction_percentages,
                    'frames_analyzed': body_rotation_stats.frames_analyzed,
                    'frames_with_detection': body_rotation_stats.frames_with_detection,
                    'detection_rate': body_rotation_stats.detection_rate,
                    'duration_seconds': body_rotation_stats.duration_seconds
                }
            else:
                results['body_rotation'] = {'error': 'Body rotation analyzer not available'}
            current_step += 1
        except Exception as e:
            print(f"Body rotation analysis failed: {e}")
            results['body_rotation'] = {'error': str(e)}
            current_step += 1
        
        # Step 2: Head Motion Analysis
        try:
            analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
            if 'head_motion' in analyzers:
                head_motion_stats = analyzers['head_motion'].process_video(video_path, target_fps=target_fps)
                results['head_motion'] = {
                    'mean_angle': head_motion_stats.mean_angle,
                    'median_angle': head_motion_stats.median_angle,
                    'std_dev_angle': head_motion_stats.std_dev_angle,
                    'min_angle': head_motion_stats.min_angle,
                    'max_angle': head_motion_stats.max_angle,
                    'dominant_direction': head_motion_stats.dominant_direction,
                    'direction_percentages': head_motion_stats.direction_percentages,
                    'stability_score': head_motion_stats.stability_score,
                    'frames_analyzed': head_motion_stats.frames_analyzed,
                    'frames_with_detection': head_motion_stats.frames_with_detection,
                    'detection_rate': head_motion_stats.detection_rate,
                    'duration_seconds': head_motion_stats.duration_seconds
                }
            else:
                results['head_motion'] = {'error': 'Head motion analyzer not available'}
            current_step += 1
        except Exception as e:
            print(f"Head motion analysis failed: {e}")
            results['head_motion'] = {'error': str(e)}
            current_step += 1
        
        # Step 3: Head Rotation Analysis
        try:
            analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
            if 'head_rotation' in analyzers:
                head_rotation_stats = analyzers['head_rotation'].process_video(video_path, target_fps=target_fps)
                results['head_rotation'] = {
                    'mean_angle': head_rotation_stats.mean_angle,
                    'median_angle': head_rotation_stats.median_angle,
                    'std_dev_angle': head_rotation_stats.std_dev_angle,
                    'dominant_direction': head_rotation_stats.dominant_direction,
                    'direction_percentages': head_rotation_stats.direction_percentages,
                    'frames_analyzed': head_rotation_stats.frames_analyzed,
                    'detection_rate': head_rotation_stats.detection_rate
                }
            else:
                results['head_rotation'] = {'error': 'Head rotation analyzer not available'}
            current_step += 1
        except Exception as e:
            print(f"Head rotation analysis failed: {e}")
            results['head_rotation'] = {'error': str(e)}
            current_step += 1
            
        # Step 4: Head Pitch Analysis
        try:
            analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
            if 'head_pitch' in analyzers:
                head_pitch_stats = analyzers['head_pitch'].process_video(video_path, target_fps=target_fps)
                results['head_pitch'] = {
                    'mean_angle': head_pitch_stats.mean_angle,
                    'median_angle': head_pitch_stats.median_angle,
                    'std_dev_angle': head_pitch_stats.std_dev_angle,
                    'dominant_direction': head_pitch_stats.dominant_direction,
                    'frames_analyzed': head_pitch_stats.frames_analyzed,
                    'detection_rate': head_pitch_stats.detection_rate
                }
            else:
                results['head_pitch'] = {'error': 'Head pitch analyzer not available'}
            current_step += 1
        except Exception as e:
            print(f"Head pitch analysis failed: {e}")
            results['head_pitch'] = {'error': str(e)}
            current_step += 1
            
        # Step 5: Hand Motion Analysis
        try:
            analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
            if 'hand_motion' in analyzers:
                hand_motion_stats = analyzers['hand_motion'].process_video(video_path, target_fps=target_fps)
                results['hand_motion'] = {
                    'activity_level': hand_motion_stats.activity_level,
                    'total_movement': hand_motion_stats.total_movement,
                    'average_movement_per_frame': hand_motion_stats.average_movement_per_frame,
                    'movement_variance': hand_motion_stats.movement_variance,
                    'frames_analyzed': hand_motion_stats.frames_analyzed,
                    'frames_with_detection': hand_motion_stats.frames_with_detection,
                    'detection_rate': hand_motion_stats.detection_rate
                }
            else:
                results['hand_motion'] = {'error': 'Hand motion analyzer not available'}
            current_step += 1
        except Exception as e:
            print(f"Hand motion analysis failed: {e}")
            results['hand_motion'] = {'error': str(e)}
            current_step += 1
            
        # Step 6: Gaze Motion Analysis
        try:
            analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
            if 'gaze_motion' in analyzers:
                gaze_motion_stats = analyzers['gaze_motion'].process_video(video_path, target_fps=target_fps)
                results['gaze_motion'] = {
                    'mean_angle': gaze_motion_stats.mean_angle,
                    'median_angle': gaze_motion_stats.median_angle,
                    'std_dev_angle': gaze_motion_stats.std_dev_angle,
                    'dominant_direction': gaze_motion_stats.dominant_direction,
                    'frames_analyzed': gaze_motion_stats.frames_analyzed,
                    'detection_rate': gaze_motion_stats.detection_rate
                }
            else:
                results['gaze_motion'] = {'error': 'Gaze motion analyzer not available'}
            current_step += 1
        except Exception as e:
            print(f"Gaze motion analysis failed: {e}")
            results['gaze_motion'] = {'error': str(e)}
            current_step += 1
            
        # Step 7: Body Tilt Analysis
        try:
            analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
            if 'body_tilt' in analyzers:
                body_tilt_stats = analyzers['body_tilt'].process_video(video_path, target_fps=target_fps)
                results['body_tilt'] = {
                    'mean_angle': body_tilt_stats.mean_angle,
                    'median_angle': body_tilt_stats.median_angle,
                    'std_dev_angle': body_tilt_stats.std_dev_angle,
                    'dominant_direction': body_tilt_stats.dominant_direction,
                    'frames_analyzed': body_tilt_stats.frames_analyzed,
                    'detection_rate': body_tilt_stats.detection_rate
                }
            else:
                results['body_tilt'] = {'error': 'Body tilt analyzer not available'}
            current_step += 1
        except Exception as e:
            print(f"Body tilt analysis failed: {e}")
            results['body_tilt'] = {'error': str(e)}
            current_step += 1
            
        # Step 8: Facial Expression Analysis
        try:
            analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
            if 'expression' in analyzers:
                expression_stats = analyzers['expression'].process_video(video_path, target_fps=target_fps)
                results['expression'] = {
                    'emotion_scores': expression_stats.emotion_scores,
                    'average_scores': expression_stats.average_scores
                }
            else:
                results['expression'] = {'error': 'Expression analyzer not available'}
            current_step += 1
        except Exception as e:
            print(f"Expression analysis failed: {e}")
            results['expression'] = {'error': str(e)}
            current_step += 1
            
        # Step 9: Audio Transcription and Content Analysis
        if 'whisper' in analyzers:
            try:
                analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
                if extract_audio_from_video(video_path, audio_path):
                    transcript = transcribe_audio(audio_path)
                    if transcript and 'content' in analyzers:
                        content_analysis = analyzers['content'].analyze_content(transcript)
                        results['content'] = content_analysis
                        results['transcript'] = transcript  # Store transcript
                    else:
                        results['content'] = {'error': 'Content analysis unavailable'}
                else:
                    results['content'] = {'error': 'Audio extraction failed'}
                current_step += 1
            except Exception as e:
                print(f"Content analysis failed: {e}")
                results['content'] = {'error': str(e)}
                current_step += 1
        else:
            results['content'] = {'error': 'Whisper model not available'}
            current_step += 1
            
        # Step 10: Disfluency Analysis
        if transcript and 'disfluency' in analyzers:
            try:
                analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
                disfluency_analysis = analyzers['disfluency'].analyze_disfluency(transcript)
                results['disfluency'] = disfluency_analysis
                current_step += 1
            except Exception as e:
                print(f"Disfluency analysis failed: {e}")
                results['disfluency'] = {'error': str(e)}
                current_step += 1
        else:
            results['disfluency'] = {'error': 'Disfluency analysis unavailable'}
            current_step += 1
            
        # Step 11: Comprehensive Presentation Evaluation
        if 'evaluator' in analyzers:
            try:
                analyses[analysis_id]['progress'] = int((current_step / total_steps) * 100)
                evaluator = analyzers['evaluator']
                evaluation_results = evaluator.evaluate_presentation(results, transcript)
                results['evaluation'] = evaluation_results
                
                # Add summary for quick access
                results['presentation_summary'] = {
                    'overall_score': evaluation_results['overall_evaluation']['overall_score'],
                    'grade': evaluation_results['overall_evaluation']['grade'],
                    'top_strengths': evaluation_results['summary']['strengths'],
                    'improvement_areas': evaluation_results['summary']['areas_for_improvement'],
                    'key_suggestions': evaluation_results['improvement_suggestions'][:3]
                }
                current_step += 1
            except Exception as e:
                print(f"Presentation evaluation failed: {e}")
                results['evaluation'] = {'error': str(e)}
                current_step += 1
        else:
            results['evaluation'] = {'error': 'Presentation evaluator not available'}
            current_step += 1
        
        # Store results and mark as completed
        analyses[analysis_id]['results'] = results
        analyses[analysis_id]['status'] = 'completed'
        analyses[analysis_id]['progress'] = 100
        
        return jsonify({'analysisId': analysis_id, 'status': 'success'})
        
    except Exception as e:
        if 'analysis_id' in locals():
            analyses[analysis_id]['status'] = 'failed'
            analyses[analysis_id]['error'] = str(e)
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
    finally:
        # Clean up temporary files
        for temp_file in [video_path, audio_path]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

@app.route('/api/analysis/<analysis_id>/status', methods=['GET'])
def get_analysis_status(analysis_id):
    """Get the status of an ongoing analysis"""
    if analysis_id not in analyses:
        return jsonify({'error': 'Analysis not found'}), 404
    
    analysis = analyses[analysis_id]
    
    response = {
        'analysisId': analysis_id,
        'status': analysis['status'],
        'progress': analysis.get('progress', 0),
        'created_at': analysis['created_at'],
        'filename': analysis['filename']
    }
    
    if analysis['status'] == 'failed' and 'error' in analysis:
        response['error'] = analysis['error']
    
    return jsonify(response)

@app.route('/api/analysis/<analysis_id>/results', methods=['GET'])
def get_analysis_results(analysis_id):
    """Get the full results of a completed analysis"""
    if analysis_id not in analyses:
        return jsonify({'error': 'Analysis not found'}), 404
    
    analysis = analyses[analysis_id]
    
    if analysis['status'] != 'completed':
        return jsonify({'error': 'Analysis not yet completed'}), 400
    
    return jsonify({
        'analysisId': analysis_id,
        **analysis['results']
    })

@app.route('/api/analysis/<analysis_id>/score', methods=['GET'])
def get_presentation_score(analysis_id):
    """Get just the presentation score and key feedback"""
    if analysis_id not in analyses:
        return jsonify({'error': 'Analysis not found'}), 404
    
    analysis = analyses[analysis_id]
    
    if analysis['status'] != 'completed':
        return jsonify({'error': 'Analysis not yet completed'}), 400
    
    results = analysis['results']
    
    # Extract presentation summary
    if 'presentation_summary' in results:
        summary = results['presentation_summary']
        evaluation = results.get('evaluation', {})
        
        return jsonify({
            'analysisId': analysis_id,
            'overall_score': summary['overall_score'],
            'grade': summary['grade'],
            'category_scores': {
                cat: eval_data['overall_score'] 
                for cat, eval_data in evaluation.get('category_evaluations', {}).items()
            },
            'strengths': summary['top_strengths'],
            'improvement_areas': summary['improvement_areas'],
            'suggestions': summary['key_suggestions'],
            'evaluation_timestamp': evaluation.get('evaluation_timestamp'),
            'filename': analysis['filename']
        })
    else:
        return jsonify({'error': 'Evaluation not available for this analysis'}), 400

@app.route('/api/analysis/<analysis_id>/detailed-feedback', methods=['GET'])
def get_detailed_feedback(analysis_id):
    """Get detailed category-wise feedback"""
    if analysis_id not in analyses:
        return jsonify({'error': 'Analysis not found'}), 404
    
    analysis = analyses[analysis_id]
    
    if analysis['status'] != 'completed':
        return jsonify({'error': 'Analysis not yet completed'}), 400
    
    results = analysis['results']
    
    if 'evaluation' in results:
        evaluation = results['evaluation']
        return jsonify({
            'analysisId': analysis_id,
            'detailed_feedback': evaluation['category_evaluations'],
            'improvement_suggestions': evaluation['improvement_suggestions'],
            'overall_evaluation': evaluation['overall_evaluation']
        })
    else:
        return jsonify({'error': 'Detailed feedback not available'}), 400

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

@app.route('/api/test', methods=['GET'])
def test_api():
    """Simple test endpoint to verify API is working"""
    analyzer_status = {}
    
    # Check which analyzers are available
    for analyzer_name in ['body_rotation', 'head_motion', 'head_rotation', 'head_pitch', 
                         'hand_motion', 'gaze_motion', 'body_tilt', 'expression', 
                         'content', 'disfluency', 'whisper', 'evaluator']:
        analyzer_status[analyzer_name] = analyzer_name in analyzers
    
    return jsonify({
        'status': 'success',
        'message': 'Auto PPT Evaluation API is working correctly',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'features': {
            'video_analysis': True,
            'audio_analysis': AUDIO_ANALYSIS_AVAILABLE,
            'ai_content_analysis': 'content' in analyzers,
            'comprehensive_evaluation': 'evaluator' in analyzers,
            'real_time_progress': True
        },
        'analyzers_available': analyzer_status,
        'dependencies': {
            'whisper_available': WHISPER_AVAILABLE,
            'moviepy_available': MOVIEPY_AVAILABLE,
            'video_analysis_available': VIDEO_ANALYSIS_AVAILABLE,
            'expression_analysis_available': EXPRESSION_ANALYSIS_AVAILABLE,
            'audio_analysis_available': AUDIO_ANALYSIS_AVAILABLE,
            'evaluation_available': EVALUATION_AVAILABLE
        },
        'api_endpoints': [
            'POST /api/analyze-video - Upload and analyze presentation video',
            'GET /api/analysis/{id}/status - Check analysis progress',
            'GET /api/analysis/{id}/results - Get full analysis results',
            'GET /api/analysis/{id}/score - Get presentation score and feedback',
            'GET /api/analysis/{id}/detailed-feedback - Get detailed category feedback',
            'GET /api/health - Health check',
            'GET /api/test - This endpoint'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print(f"🚀 Starting Auto PPT Evaluation Backend in {Config.FLASK_ENV} mode")
    app.run(debug=Config.DEBUG, port=5000, host='0.0.0.0')