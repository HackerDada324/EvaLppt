from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class AnalysisResult:
    """Results from analyzing a single frame"""
    status: str = ""
    angle: float = 0.0
    direction: str = ""
    landmarks: Dict = None
    frame_number: int = 0
    timestamp: float = 0.0
    additional_info: Dict = None
    emotion: str = ""
    confidence: float = 0.0
    sentiment: str = ""
    emotion_probabilities: Dict[str, float] = None  # Add this line

@dataclass
class VideoAnalysisStats:
    """Statistical summary of video analysis"""
    mean_angle: float = 0.0
    median_angle: float = 0.0
    std_dev_angle: float = 0.0
    min_angle: float = 0.0
    max_angle: float = 0.0
    dominant_direction: str = ""
    direction_percentages: Dict[str, float] = None
    stability_score: float = 0.0
    frames_analyzed: int = 0
    frames_with_detection: int = 0
    detection_rate: float = 0.0
    duration_seconds: float = 0.0
    additional_stats: Dict = None
    movement_score: float = 0.0  
    avg_hands_per_frame: float = 0.0  
    processing_time: float = 0.0  
    processing_fps: float = 0.0  
    excessive_motion_rate: float = 0.0
    emotion: str = ""
    confidence: float = 0.0
    sentiment: str = ""
    dominant_emotion: str = ""
    emotion_percentages: Dict[str, float] = None
    mean_confidence: float = 0.0
    overall_sentiment: float = 0.0
    sentiment_score: float = 0.0