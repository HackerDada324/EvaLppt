import cv2
import math
import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import mediapipe as mp
from posture_analysis.core.base import MotionAnalyzer
from posture_analysis.core.data_models import AnalysisResult, VideoAnalysisStats

class BodyMotionAnalyzer(MotionAnalyzer):
    """Analyzer for body alignment and tilt relative to vertical axis, with minimal processing"""
    
    def __init__(self, min_detection_confidence: float = 0.7, tilt_threshold: float = 5):
        super().__init__(min_detection_confidence)
        self.tilt_threshold = tilt_threshold
        self.mp_pose = mp.solutions.pose
    
    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[AnalysisResult]:
        """Analyze a single frame for body alignment statistics only"""
        # Initialize Pose model
        with self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=self.min_detection_confidence
        ) as pose:
            results = pose.process(image_rgb)
            
            if not results.pose_landmarks:
                return None
            
            # Get relevant landmarks
            landmarks = results.pose_landmarks.landmark
            
            # Extract key points for posture analysis
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
            
            # Calculate image dimensions (needed for conversion to pixel coordinates)
            h, w = image_rgb.shape[:2]
            
            # Convert normalized coordinates to pixel coordinates
            left_shoulder_px = (int(left_shoulder.x * w), int(left_shoulder.y * h))
            right_shoulder_px = (int(right_shoulder.x * w), int(right_shoulder.y * h))
            left_hip_px = (int(left_hip.x * w), int(left_hip.y * h))
            right_hip_px = (int(right_hip.x * w), int(right_hip.y * h))
            
            # Calculate midpoints
            shoulder_midpoint = (
                (left_shoulder_px[0] + right_shoulder_px[0]) // 2, 
                (left_shoulder_px[1] + right_shoulder_px[1]) // 2
            )
            hip_midpoint = (
                (left_hip_px[0] + right_hip_px[0]) // 2, 
                (left_hip_px[1] + right_hip_px[1]) // 2
            )
            
            # Calculate the angle between spine and perpendicular axis
            dx = shoulder_midpoint[0] - hip_midpoint[0]
            dy = shoulder_midpoint[1] - hip_midpoint[1]
            
            # Calculate angle with perpendicular axis
            if dx == 0:  # Perfectly aligned with perpendicular
                spine_angle = 0
            else:
                # Calculate angle in radians and convert to degrees
                spine_angle = math.degrees(math.atan2(dx, dy))
            
            # Normalize to 0-90 degrees
            spine_angle = abs(spine_angle)
            if spine_angle > 90:
                spine_angle = 180 - spine_angle
            
            # Determine tilt direction
            if shoulder_midpoint[0] > hip_midpoint[0]:
                tilt_direction = "right"
            elif shoulder_midpoint[0] < hip_midpoint[0]:
                tilt_direction = "left"
            else:
                tilt_direction = "none"
            
            # Determine alignment status
            if spine_angle < self.tilt_threshold:
                alignment_status = "Vertical"
            else:
                alignment_status = f"Tilted {tilt_direction} by {spine_angle:.2f} degrees"
            
            # Store landmarks
            landmarks_dict = {
                "left_shoulder": left_shoulder_px,
                "right_shoulder": right_shoulder_px,
                "left_hip": left_hip_px,
                "right_hip": right_hip_px,
                "shoulder_midpoint": shoulder_midpoint,
                "hip_midpoint": hip_midpoint
            }
            
            # Create analysis result
            result = AnalysisResult(
                status=alignment_status,
                angle=spine_angle,
                direction=tilt_direction,
                landmarks=landmarks_dict
            )
            
            return result
    
    def process_video(self, video_path: str, sampling_rate: int = 1, show_progress: bool = True) -> VideoAnalysisStats:
        """
        Process video and analyze body alignment frame by frame, only collecting statistics
        
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
        angles = []
        directions = []
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
                    angles.append(result.angle)
                    directions.append(result.direction)
                    timestamps.append(frame_index / fps)
                    
                    # Set frame metadata
                    result.frame_number = frame_index
                    result.timestamp = frame_index / fps
                    
                    frame_results.append({
                        "frame": frame_index,
                        "timestamp": frame_index / fps,
                        "angle": result.angle,
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
        if angles:
            # Basic statistics
            mean_angle = np.mean(angles)
            median_angle = np.median(angles)
            std_dev_angle = np.std(angles)
            min_angle = np.min(angles)
            max_angle = np.max(angles)
            
            # Direction analysis
            direction_counts = {dir: directions.count(dir) for dir in set(directions)}
            total_directions = len(directions)
            direction_percentages = {dir: (count / total_directions) * 100 
                                    for dir, count in direction_counts.items()}
            
            # Find dominant direction
            dominant_direction = max(direction_counts, key=direction_counts.get)
            
            # Calculate stability score (lower means more stable)
            stability_score = std_dev_angle
            
            # Calculate detection rate
            detection_rate = frames_with_detection / (frame_count / sampling_rate) * 100
            
            # Create statistics object
            stats = VideoAnalysisStats(
                mean_angle=mean_angle,
                median_angle=median_angle,
                std_dev_angle=std_dev_angle,
                min_angle=min_angle,
                max_angle=max_angle,
                dominant_direction=dominant_direction,
                direction_percentages=direction_percentages,
                stability_score=stability_score,
                frames_analyzed=frame_index,
                frames_with_detection=frames_with_detection,
                detection_rate=detection_rate,
                duration_seconds=duration
            )
            
            # Print summary
            print(f"\nBody Alignment Analysis Complete for {video_path}")
            print(f"- Duration: {duration:.2f} seconds")
            print(f"- Frames processed: {frames_with_detection}/{frame_index} ({detection_rate:.2f}%)")
            print(f"- Average tilt angle: {mean_angle:.2f}° ± {std_dev_angle:.2f}°")
            print(f"- Dominant tilt direction: {dominant_direction}")
            print(f"- Stability score: {stability_score:.2f} (lower is more stable)")
            print(f"- Processing time: {processing_time:.2f} seconds ({processing_fps:.2f} FPS)")
            
            return stats
        else:
            print("No valid detection in video frames. Unable to generate statistics.")
            return None