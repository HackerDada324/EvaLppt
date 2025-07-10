"""
Video processing utilities for the Auto PPT Evaluation System
"""
import os
from typing import Dict, Any, Optional

from .exceptions import ProcessingError


class VideoProcessor:
    """Handles video processing operations"""
    
    def __init__(self):
        """Initialize video processor"""
        # Check for moviepy availability
        try:
            import moviepy.editor as mp
            self.moviepy = mp
            self.moviepy_available = True
        except ImportError:
            self.moviepy = None
            self.moviepy_available = False
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video file information
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary with video information
            
        Raises:
            ProcessingError: If unable to get video info
        """
        if not os.path.exists(video_path):
            raise ProcessingError(f"Video file not found: {video_path}")
        
        video_info = {
            'file_path': video_path,
            'file_size_mb': os.path.getsize(video_path) / (1024 * 1024),
            'filename': os.path.basename(video_path)
        }
        
        if self.moviepy_available:
            try:
                video = self.moviepy.VideoFileClip(video_path)
                video_info.update({
                    'duration_seconds': video.duration,
                    'fps': video.fps,
                    'width': video.w,
                    'height': video.h,
                    'aspect_ratio': video.w / video.h if video.h > 0 else 0
                })
                video.close()
            except Exception as e:
                print(f"Warning: Could not extract video metadata: {e}")
        
        return video_info
    
    def validate_video_for_processing(self, video_path: str) -> bool:
        """
        Validate if video can be processed
        
        Args:
            video_path: Path to the video file
            
        Returns:
            True if video is valid for processing
            
        Raises:
            ProcessingError: If video is invalid
        """
        if not os.path.exists(video_path):
            raise ProcessingError(f"Video file not found: {video_path}")
        
        if not self.moviepy_available:
            # Basic file existence check if moviepy not available
            return True
        
        try:
            video = self.moviepy.VideoFileClip(video_path)
            
            # Check if video has required properties
            if video.duration is None or video.duration <= 0:
                raise ProcessingError("Video has no duration or invalid duration")
            
            if video.fps is None or video.fps <= 0:
                raise ProcessingError("Video has invalid frame rate")
            
            video.close()
            return True
            
        except Exception as e:
            raise ProcessingError(f"Video validation failed: {e}")
    
    def calculate_target_frame_interval(self, video_path: str, target_fps: float = 5.0) -> float:
        """
        Calculate frame interval for target FPS
        
        Args:
            video_path: Path to the video file
            target_fps: Target frames per second for analysis
            
        Returns:
            Frame interval in seconds
            
        Raises:
            ProcessingError: If unable to calculate interval
        """
        if not self.moviepy_available:
            # Default fallback
            return 1.0 / target_fps
        
        try:
            video = self.moviepy.VideoFileClip(video_path)
            original_fps = video.fps
            video.close()
            
            if original_fps <= 0:
                return 1.0 / target_fps
            
            # Calculate how many original frames to skip
            skip_frames = max(1, int(original_fps / target_fps))
            return skip_frames / original_fps
            
        except Exception as e:
            print(f"Warning: Could not calculate frame interval: {e}")
            return 1.0 / target_fps
