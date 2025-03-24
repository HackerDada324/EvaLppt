import cv2
import math
import numpy as np
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Union
import mediapipe as mp

@dataclass
class AnalysisResult:
    """Data class to store results of a single frame analysis"""
    status: str
    angle: float
    direction: str
    landmarks: Dict = field(default_factory=dict)
    frame_number: Optional[int] = None
    timestamp: Optional[float] = None
    additional_info: Dict = field(default_factory=dict)

@dataclass
class VideoAnalysisStats:
    """Data class to store statistical results of video analysis"""
    dominant_direction: str
    direction_percentages: Dict[str, float]
    frames_analyzed: int
    frames_with_detection: int
    detection_rate: float
    duration_seconds: float
    additional_stats: Dict = field(default_factory=dict)
    mean_angle: float = 0.0
    median_angle: float = 0.0
    std_dev_angle: float = 0.0
    min_angle: float = 0.0
    max_angle: float = 0.0
    stability_score: float = 0.0

class GazeMotionAnalyzer:
    """Analyzer for eye gaze using GazeTracking library"""
    
    def __init__(self, min_detection_confidence: float = 0.5):
        self.min_detection_confidence = min_detection_confidence
    
    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[AnalysisResult]:
        """Analyze a single frame for gaze statistics only"""
        # Import GazeTracking here to avoid dependency issues
        from gaze_tracker.gaze_tracking import GazeTracking
        
        # Initialize gaze tracking
        gaze = GazeTracking()
        
        # Convert RGB to BGR for GazeTracking (if needed)
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Use GazeTracking for eye gaze detection
        gaze.refresh(image_bgr)
        
        # Check if gaze detection was successful
        if not gaze.pupils_located:
            return None
        
        # Get gaze information
        if gaze.is_right():
            gaze_direction = "right"
            gaze_text = "Looking right"
        elif gaze.is_left():
            gaze_direction = "left"
            gaze_text = "Looking left"
        elif gaze.is_center():
            gaze_direction = "center"
            gaze_text = "Looking center"
        else:
            gaze_direction = "uncertain"
            gaze_text = "Gaze direction uncertain"
        
        # Get pupil positions if detected
        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
        
        # Calculate eye contact status
        if gaze.is_center():
            eye_contact_status = "Maintaining eye contact"
        else:
            eye_contact_status = "Not maintaining eye contact"
        
        # Store landmarks and additional info
        landmarks_dict = {}
        if left_pupil:
            landmarks_dict["left_pupil"] = left_pupil
        if right_pupil:
            landmarks_dict["right_pupil"] = right_pupil
            
        additional_info = {
            "eye_contact": eye_contact_status,
            "gaze_text": gaze_text
        }
        
        # Create analysis result
        result = AnalysisResult(
            status=eye_contact_status,
            angle=0.0,  # No angle measurement for gaze
            direction=gaze_direction,
            landmarks=landmarks_dict,
            additional_info=additional_info
        )
        
        return result
    
    def analyze(self, image: np.ndarray) -> AnalysisResult:
        """Analyze a single image and return results only (no drawing)"""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Analyze frame
        result = self._analyze_frame(image_rgb)
        
        return result
    
    def process_video(self, video_path: str, target_fps: Optional[float] = None, show_progress: bool = True) -> VideoAnalysisStats:
        """
        Process video and analyze gaze frame by frame, only collecting statistics
        
        Args:
            video_path: Path to the video file
            target_fps: Target frames per second for analysis; if None, uses original video FPS
            show_progress: Whether to display a progress bar during processing
            
        Returns:
            VideoAnalysisStats: Statistical summary of analysis
        """
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Error: Could not open video at {video_path}")
        
        # Get video properties
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / original_fps if original_fps > 0 else 0
        
        # Determine processing FPS and calculate frame skipping
        processing_fps = original_fps if target_fps is None else target_fps
        
        # Calculate frames to skip
        if processing_fps >= original_fps:
            # If target FPS is higher or equal to original, process every frame
            frame_interval = 1
        else:
            # Skip frames to match desired FPS
            frame_interval = int(original_fps / processing_fps)
        
        # Variables to store analysis results
        directions = []
        eye_contact_counts = {"Maintaining eye contact": 0, "Not maintaining eye contact": 0}
        timestamps = []
        frames_with_detection = 0
        frame_results = []
        
        # Start timing
        start_time = time.time()
        
        # Process frames
        frame_index = 0
        
        # Create progress bar if requested
        if show_progress:
            try:
                from tqdm import tqdm
                pbar = tqdm(total=frame_count, desc="Processing video")
            except ImportError:
                show_progress = False
                print("tqdm not installed, progress bar disabled")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process frames based on calculated interval
            if frame_index % frame_interval == 0:
                # Process the frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self._analyze_frame(frame_rgb)
                
                if result is not None:
                    frames_with_detection += 1
                    directions.append(result.direction)
                    timestamps.append(frame_index / original_fps)
                    eye_contact_counts[result.status] += 1
                    
                    # Set frame metadata
                    result.frame_number = frame_index
                    result.timestamp = frame_index / original_fps
                    
                    frame_results.append({
                        "frame": frame_index,
                        "timestamp": frame_index / original_fps,
                        "direction": result.direction,
                        "status": result.status
                    })
            
            frame_index += 1
            
            # Update progress bar
            if show_progress:
                pbar.update(1)
        
        # Close progress bar
        if show_progress:
            pbar.close()
            
        # Calculate processing time
        processing_time = time.time() - start_time
        effective_fps = frame_count / processing_time
        
        # Release resources
        cap.release()
        
        # Calculate statistics only if we have enough data
        if directions:
            # Direction analysis
            direction_counts = {dir: directions.count(dir) for dir in set(directions)}
            total_directions = len(directions)
            direction_percentages = {dir: (count / total_directions) * 100 
                                    for dir, count in direction_counts.items()}
            
            # Find dominant direction
            dominant_direction = max(direction_counts, key=direction_counts.get)
            
            # Calculate eye contact percentage
            total_frames_with_detection = sum(eye_contact_counts.values())
            eye_contact_percentage = (eye_contact_counts["Maintaining eye contact"] / 
                                      total_frames_with_detection * 100) if total_frames_with_detection > 0 else 0
            
            # Calculate detection rate
            frames_expected = frame_count // frame_interval
            detection_rate = frames_with_detection / frames_expected * 100
            
            # Create statistics object
            stats = VideoAnalysisStats(
                dominant_direction=dominant_direction,
                direction_percentages=direction_percentages,
                frames_analyzed=frame_index,
                frames_with_detection=frames_with_detection,
                detection_rate=detection_rate,
                duration_seconds=duration,
                additional_stats={
                    "eye_contact_percentage": eye_contact_percentage,
                    "eye_contact_frames": eye_contact_counts["Maintaining eye contact"],
                    "no_eye_contact_frames": eye_contact_counts["Not maintaining eye contact"],
                    "original_fps": original_fps,
                    "target_fps": processing_fps,
                    "frame_interval": frame_interval
                }
            )
            
            # Print summary
            print(f"\nGaze Analysis Complete for {video_path}")
            print(f"- Duration: {duration:.2f} seconds")
            print(f"- Original video FPS: {original_fps:.2f}")
            print(f"- Target processing FPS: {processing_fps:.2f}")
            print(f"- Frames processed: {frames_with_detection}/{frames_expected} ({detection_rate:.2f}%)")
            print(f"- Dominant gaze direction: {dominant_direction}")
            print(f"- Eye contact maintained: {eye_contact_percentage:.2f}% of detected frames")
            print(f"- Direction breakdown: {direction_percentages}")
            print(f"- Processing time: {processing_time:.2f} seconds ({effective_fps:.2f} FPS)")
            
            return stats
        else:
            print("No valid gaze detection in video frames. Unable to generate statistics.")
            return None