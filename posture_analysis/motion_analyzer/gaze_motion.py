import cv2
import math
import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Union
import mediapipe as mp
from ..core.base import MotionAnalyzer
from ..core.data_models import AnalysisResult, VideoAnalysisStats


class GazeMotionAnalyzer(MotionAnalyzer):
    """Analyzer for eye gaze using GazeTracking library"""
    
    def __init__(self, min_detection_confidence: float = 0.5):
        super().__init__(min_detection_confidence)
        # GazeTracking will be imported during processing to avoid dependency issues
    
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
    
    def process_video(self, video_path: str, sampling_rate: int = 1, show_progress: bool = True) -> VideoAnalysisStats:
        """
        Process video and analyze gaze frame by frame, only collecting statistics
        
        Args:
            video_path: Path to the video file
            sampling_rate: Process every Nth frame (1 = every frame, 2 = every other frame, etc.)
            show_progress: Whether to display a progress bar during processing
            
        Returns:
            VideoAnalysisStats: Statistical summary of analysis
        """
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Error: Could not open video at {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
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
                
            # Process every Nth frame based on sampling rate
            if frame_index % sampling_rate == 0:
                # Process the frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self._analyze_frame(frame_rgb)
                
                if result is not None:
                    frames_with_detection += 1
                    directions.append(result.direction)
                    timestamps.append(frame_index / fps)
                    eye_contact_counts[result.status] += 1
                    
                    # Set frame metadata
                    result.frame_number = frame_index
                    result.timestamp = frame_index / fps
                    
                    frame_results.append({
                        "frame": frame_index,
                        "timestamp": frame_index / fps,
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
        processing_fps = frame_count / processing_time
        
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
            detection_rate = frames_with_detection / (frame_count / sampling_rate) * 100
            
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
                    "no_eye_contact_frames": eye_contact_counts["Not maintaining eye contact"]
                }
            )
            
            # Print summary
            print(f"\nGaze Analysis Complete for {video_path}")
            print(f"- Duration: {duration:.2f} seconds")
            print(f"- Frames processed: {frames_with_detection}/{frame_index} ({detection_rate:.2f}%)")
            print(f"- Dominant gaze direction: {dominant_direction}")
            print(f"- Eye contact maintained: {eye_contact_percentage:.2f}% of detected frames")
            print(f"- Direction breakdown: {direction_percentages}")
            print(f"- Processing time: {processing_time:.2f} seconds ({processing_fps:.2f} FPS)")
            
            return stats
        else:
            print("No valid gaze detection in video frames. Unable to generate statistics.")
            return None