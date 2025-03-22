from dataclasses import dataclass
from typing import Dict

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