"""
Video Analysis Service - Handles comprehensive video analysis workflow
"""
import os
import tempfile
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import traceback

from ..models.analysis import AnalysisRecord, AnalysisStatus
from ..models.presentation import PresentationResult, MotionAnalysisResult, ExpressionAnalysisResult, AudioAnalysisResult, PresentationScore
from ..utils.file_handler import FileHandler
from ..utils.audio_processor import AudioProcessor
from ..utils.video_processor import VideoProcessor
from ..utils.exceptions import ProcessingError, ValidationError
from .analyzer_service import AnalyzerService


class VideoAnalysisService:
    """Service for coordinating comprehensive video analysis workflow"""
    
    def __init__(self, analyzer_service: AnalyzerService):
        """
        Initialize video analysis service
        
        Args:
            analyzer_service: Initialized analyzer service instance
        """
        self.analyzer_service = analyzer_service
        self.file_handler = FileHandler()
        self.video_processor = VideoProcessor()
        
        # Initialize audio processor with Whisper model
        whisper_model = self.analyzer_service.get_analyzer('whisper')
        self.audio_processor = AudioProcessor(whisper_model)
    
    def analyze_video_file(self, video_file, target_fps: float = 5.0) -> str:
        """
        Perform comprehensive video analysis
        
        Args:
            video_file: Uploaded video file object
            target_fps: Target frames per second for analysis
            
        Returns:
            Analysis ID for tracking progress
            
        Raises:
            ValidationError: If file validation fails
            ProcessingError: If processing fails
        """
        # Create analysis record
        analysis_record = self.analyzer_service.create_analysis_record(video_file.filename)
        analysis_id = analysis_record.analysis_id
        
        try:
            # Save uploaded file and prepare paths
            video_path, audio_path = self.file_handler.save_uploaded_video(video_file)
            
            # Add file metadata
            file_info = self.file_handler.get_file_info(video_path)
            analysis_record.add_metadata('file_info', file_info)
            
            # Update status to processing
            analysis_record.update_status(AnalysisStatus.PROCESSING)
            
            # Perform analysis
            results = self._perform_comprehensive_analysis(
                analysis_id, video_path, audio_path, target_fps
            )
            
            # Set final results
            self.analyzer_service.set_analysis_results(analysis_id, results)
            
            return analysis_id
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.analyzer_service.set_analysis_error(analysis_id, error_msg)
            raise ProcessingError(error_msg) from e
        
        finally:
            # Clean up temporary files
            if 'video_path' in locals() and 'audio_path' in locals():
                self.file_handler.cleanup_files(video_path, audio_path)
    
    def _perform_comprehensive_analysis(self, analysis_id: str, video_path: str, 
                                       audio_path: str, target_fps: float) -> Dict[str, Any]:
        """
        Perform the actual comprehensive analysis
        
        Args:
            analysis_id: Analysis ID for progress tracking
            video_path: Path to video file
            audio_path: Path for audio extraction
            target_fps: Target FPS for analysis
            
        Returns:
            Dictionary with all analysis results
        """
        results = {}
        total_steps = 11
        current_step = 0
        transcript = None
        
        # Video motion analysis steps (7 steps)
        motion_analyzers = [
            ('body_rotation', 'Body Rotation Analysis'),
            ('head_motion', 'Head Motion Analysis'),
            ('head_rotation', 'Head Rotation Analysis'),
            ('head_pitch', 'Head Pitch Analysis'),
            ('hand_motion', 'Hand Motion Analysis'),
            ('gaze_motion', 'Gaze Motion Analysis'),
            ('body_tilt', 'Body Tilt Analysis')
        ]
        
        for analyzer_name, step_name in motion_analyzers:
            try:
                self._update_progress(analysis_id, current_step, total_steps)
                
                if self.analyzer_service.is_analyzer_available(analyzer_name):
                    analyzer = self.analyzer_service.get_analyzer(analyzer_name)
                    stats = analyzer.process_video(video_path, target_fps=target_fps)
                    results[analyzer_name] = self._convert_motion_stats_to_dict(stats)
                else:
                    results[analyzer_name] = {'error': f'{step_name} not available'}
                
                current_step += 1
                
            except Exception as e:
                print(f"{step_name} failed: {e}")
                results[analyzer_name] = {'error': str(e)}
                current_step += 1
        
        # Facial expression analysis (1 step)
        try:
            self._update_progress(analysis_id, current_step, total_steps)
            
            if self.analyzer_service.is_analyzer_available('expression'):
                analyzer = self.analyzer_service.get_analyzer('expression')
                expression_stats = analyzer.process_video(video_path, target_fps=target_fps)
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
        
        # Audio transcription and content analysis (1 step)
        try:
            self._update_progress(analysis_id, current_step, total_steps)
            
            if self.analyzer_service.is_analyzer_available('whisper'):
                # Extract audio and transcribe
                if self.audio_processor.extract_audio_from_video(video_path, audio_path):
                    transcript = self.audio_processor.transcribe_audio(audio_path)
                    
                    if transcript and self.analyzer_service.is_analyzer_available('content'):
                        content_analyzer = self.analyzer_service.get_analyzer('content')
                        content_analysis = content_analyzer.analyze_content(transcript)
                        results['content'] = content_analysis
                        results['transcript'] = transcript
                    else:
                        results['content'] = {'error': 'Content analysis unavailable'}
                else:
                    results['content'] = {'error': 'Audio extraction failed'}
            else:
                results['content'] = {'error': 'Whisper model not available'}
            
            current_step += 1
            
        except Exception as e:
            print(f"Content analysis failed: {e}")
            results['content'] = {'error': str(e)}
            current_step += 1
        
        # Disfluency analysis (1 step)
        try:
            self._update_progress(analysis_id, current_step, total_steps)
            
            if transcript and self.analyzer_service.is_analyzer_available('disfluency'):
                disfluency_analyzer = self.analyzer_service.get_analyzer('disfluency')
                disfluency_analysis = disfluency_analyzer.analyze_disfluency(transcript)
                results['disfluency'] = disfluency_analysis
            else:
                results['disfluency'] = {'error': 'Disfluency analysis unavailable'}
            
            current_step += 1
            
        except Exception as e:
            print(f"Disfluency analysis failed: {e}")
            results['disfluency'] = {'error': str(e)}
            current_step += 1
        
        # Comprehensive evaluation (1 step)
        try:
            self._update_progress(analysis_id, current_step, total_steps)
            
            if self.analyzer_service.is_analyzer_available('evaluator'):
                evaluator = self.analyzer_service.get_analyzer('evaluator')
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
            else:
                results['evaluation'] = {'error': 'Presentation evaluator not available'}
            
            current_step += 1
            
        except Exception as e:
            print(f"Presentation evaluation failed: {e}")
            results['evaluation'] = {'error': str(e)}
            current_step += 1
        
        # Final progress update
        self._update_progress(analysis_id, total_steps, total_steps)
        
        return results
    
    def _update_progress(self, analysis_id: str, current_step: int, total_steps: int):
        """Update analysis progress"""
        progress = int((current_step / total_steps) * 100)
        self.analyzer_service.update_analysis_progress(analysis_id, progress)
    
    def _convert_motion_stats_to_dict(self, stats) -> Dict[str, Any]:
        """
        Convert motion analysis stats object to dictionary
        
        Args:
            stats: Motion analysis statistics object
            
        Returns:
            Dictionary representation of stats
        """
        result = {
            'frames_analyzed': getattr(stats, 'frames_analyzed', 0),
            'frames_with_detection': getattr(stats, 'frames_with_detection', 0),
            'detection_rate': getattr(stats, 'detection_rate', 0.0)
        }
        
        # Add angle-related fields if they exist
        angle_fields = ['mean_angle', 'median_angle', 'std_dev_angle', 'min_angle', 'max_angle']
        for field in angle_fields:
            if hasattr(stats, field):
                result[field] = getattr(stats, field)
        
        # Add rotation-specific fields
        rotation_fields = ['mean_rotation_angle', 'median_rotation_angle', 'std_dev_rotation_angle', 
                          'min_rotation_angle', 'max_rotation_angle', 'dominant_rotation_direction',
                          'rotation_direction_percentages']
        for field in rotation_fields:
            if hasattr(stats, field):
                result[field] = getattr(stats, field)
        
        # Add direction and motion fields
        direction_fields = ['dominant_direction', 'direction_percentages', 'stability_score']
        for field in direction_fields:
            if hasattr(stats, field):
                result[field] = getattr(stats, field)
        
        # Add hand motion specific fields
        motion_fields = ['activity_level', 'total_movement', 'average_movement_per_frame', 'movement_variance']
        for field in motion_fields:
            if hasattr(stats, field):
                result[field] = getattr(stats, field)
        
        # Add duration if available
        if hasattr(stats, 'duration_seconds'):
            result['duration_seconds'] = stats.duration_seconds
        
        return result
    
    def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis status
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Status information or None if not found
        """
        record = self.analyzer_service.get_analysis_record(analysis_id)
        if not record:
            return None
        
        return {
            'analysisId': analysis_id,
            'status': record.status.value,
            'progress': record.progress,
            'created_at': record.created_at.isoformat(),
            'filename': record.filename,
            'error_message': record.error_message
        }
    
    def get_analysis_results(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full analysis results
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Full results or None if not found/completed
        """
        record = self.analyzer_service.get_analysis_record(analysis_id)
        if not record or record.status != AnalysisStatus.COMPLETED:
            return None
        
        results = record.results.copy() if record.results else {}
        results['analysisId'] = analysis_id
        return results
    
    def get_presentation_score(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get presentation score and key feedback
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Score information or None if not available
        """
        record = self.analyzer_service.get_analysis_record(analysis_id)
        if not record or record.status != AnalysisStatus.COMPLETED or not record.results:
            return None
        
        results = record.results
        
        if 'presentation_summary' in results:
            summary = results['presentation_summary']
            evaluation = results.get('evaluation', {})
            
            return {
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
                'filename': record.filename
            }
        
        return None
    
    def get_detailed_feedback(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed category-wise feedback
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Detailed feedback or None if not available
        """
        record = self.analyzer_service.get_analysis_record(analysis_id)
        if not record or record.status != AnalysisStatus.COMPLETED or not record.results:
            return None
        
        results = record.results
        
        if 'evaluation' in results:
            evaluation = results['evaluation']
            return {
                'analysisId': analysis_id,
                'detailed_feedback': evaluation['category_evaluations'],
                'improvement_suggestions': evaluation['improvement_suggestions'],
                'overall_evaluation': evaluation['overall_evaluation']
            }
        
        return None
