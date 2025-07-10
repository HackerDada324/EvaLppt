"""
Presentation Result Models for structured data representation
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class PresentationScore:
    """Model for presentation scoring data"""
    overall_score: float
    grade: str
    category_scores: Dict[str, float] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    evaluation_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'overall_score': self.overall_score,
            'grade': self.grade,
            'category_scores': self.category_scores,
            'strengths': self.strengths,
            'improvement_areas': self.improvement_areas,
            'suggestions': self.suggestions,
            'evaluation_timestamp': self.evaluation_timestamp.isoformat()
        }


@dataclass
class MotionAnalysisResult:
    """Model for motion analysis results"""
    analyzer_type: str
    mean_angle: Optional[float] = None
    median_angle: Optional[float] = None
    std_dev_angle: Optional[float] = None
    dominant_direction: Optional[str] = None
    frames_analyzed: int = 0
    detection_rate: float = 0.0
    stability_score: Optional[float] = None
    activity_level: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'analyzer_type': self.analyzer_type,
            'frames_analyzed': self.frames_analyzed,
            'detection_rate': self.detection_rate,
            'metadata': self.metadata
        }
        
        # Add optional fields if they exist
        if self.mean_angle is not None:
            result['mean_angle'] = self.mean_angle
        if self.median_angle is not None:
            result['median_angle'] = self.median_angle
        if self.std_dev_angle is not None:
            result['std_dev_angle'] = self.std_dev_angle
        if self.dominant_direction is not None:
            result['dominant_direction'] = self.dominant_direction
        if self.stability_score is not None:
            result['stability_score'] = self.stability_score
        if self.activity_level is not None:
            result['activity_level'] = self.activity_level
            
        return result


@dataclass
class ExpressionAnalysisResult:
    """Model for facial expression analysis results"""
    emotion_scores: Dict[str, float] = field(default_factory=dict)
    average_scores: Dict[str, float] = field(default_factory=dict)
    dominant_emotion: Optional[str] = None
    emotion_timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'emotion_scores': self.emotion_scores,
            'average_scores': self.average_scores,
            'dominant_emotion': self.dominant_emotion,
            'emotion_timeline': self.emotion_timeline
        }


@dataclass
class AudioAnalysisResult:
    """Model for audio analysis results"""
    transcript: Optional[str] = None
    content_analysis: Dict[str, Any] = field(default_factory=dict)
    disfluency_analysis: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0
    word_count: int = 0
    speaking_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'transcript': self.transcript,
            'content_analysis': self.content_analysis,
            'disfluency_analysis': self.disfluency_analysis,
            'duration_seconds': self.duration_seconds,
            'word_count': self.word_count,
            'speaking_rate': self.speaking_rate
        }


@dataclass
class PresentationResult:
    """
    Comprehensive model for presentation analysis results
    """
    analysis_id: str
    filename: str
    motion_results: Dict[str, MotionAnalysisResult] = field(default_factory=dict)
    expression_result: Optional[ExpressionAnalysisResult] = None
    audio_result: Optional[AudioAnalysisResult] = None
    presentation_score: Optional[PresentationScore] = None
    processing_time_seconds: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = {
            'analysis_id': self.analysis_id,
            'filename': self.filename,
            'processing_time_seconds': self.processing_time_seconds,
            'created_at': self.created_at.isoformat(),
            'motion_results': {
                key: motion.to_dict() for key, motion in self.motion_results.items()
            }
        }
        
        if self.expression_result:
            result['expression_result'] = self.expression_result.to_dict()
        
        if self.audio_result:
            result['audio_result'] = self.audio_result.to_dict()
        
        if self.presentation_score:
            result['presentation_score'] = self.presentation_score.to_dict()
        
        return result
    
    def add_motion_result(self, analyzer_name: str, motion_result: MotionAnalysisResult):
        """Add motion analysis result"""
        self.motion_results[analyzer_name] = motion_result
    
    def set_expression_result(self, expression_result: ExpressionAnalysisResult):
        """Set expression analysis result"""
        self.expression_result = expression_result
    
    def set_audio_result(self, audio_result: AudioAnalysisResult):
        """Set audio analysis result"""
        self.audio_result = audio_result
    
    def set_presentation_score(self, presentation_score: PresentationScore):
        """Set presentation score"""
        self.presentation_score = presentation_score
