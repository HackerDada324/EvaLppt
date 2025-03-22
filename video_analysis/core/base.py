import cv2
import numpy as np
import time
from typing import Tuple, Optional, Dict, Any, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from .data_models import AnalysisResult, VideoAnalysisStats

class MotionAnalyzer:
    """Base class for all motion analyzers"""
    
    def __init__(self, min_detection_confidence: float = 0.5):
        self.min_detection_confidence = min_detection_confidence
        
    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[AnalysisResult]:
        """
        Analyze a single frame and return the analysis results
        
        This is the core method that must be implemented by all subclasses
        
        Args:
            image_rgb: RGB format image as numpy array
            
        Returns:
            AnalysisResult: Analysis results or None if no detection
        """
        raise NotImplementedError("Subclasses must implement _analyze_frame method")
    
    def analyze(self, image: np.ndarray) -> Optional[AnalysisResult]:
        """Analyze a single image and return results only (no drawing)"""
        # Convert BGR to RGB if needed
        if image.shape[2] == 3 and image.dtype == np.uint8:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
        
        # Analyze frame
        result = self._analyze_frame(image_rgb)
        
        return result