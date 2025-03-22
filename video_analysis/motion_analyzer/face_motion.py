import cv2
import math
import numpy as np
import time
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
import mediapipe as mp


@dataclass
class AnalysisResult:
    """Data class to store results of a single frame analysis"""
    status: str
    angle: float
    direction: str
    landmarks: Dict
    frame_number: int = None
    timestamp: float = None

@dataclass
class VideoAnalysisStats:
    """Data class to store statistical results of video analysis"""
    mean_angle: float
    median_angle: float
    std_dev_angle: float
    min_angle: float
    max_angle: float
    dominant_direction: str
    direction_percentages: Dict[str, float]
    stability_score: float
    frames_analyzed: int
    frames_with_detection: int
    detection_rate: float
    duration_seconds: float

class FaceMotionAnalyzer:
    """Analyzer for face tilt using MediaPipe Face Mesh"""
    
    def __init__(self, min_detection_confidence: float = 0.5, tilt_threshold: float = 5):
        self.min_detection_confidence = min_detection_confidence
        self.tilt_threshold = tilt_threshold
        self.mp_face_mesh = mp.solutions.face_mesh
    
    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[AnalysisResult]:
        """Analyze a single frame for face tilt statistics only"""
        # Initialize Face Mesh
        with self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=self.min_detection_confidence
        ) as face_mesh:
            results = face_mesh.process(image_rgb)
            
            if not results.multi_face_landmarks:
                return None
            
            face_landmarks = results.multi_face_landmarks[0]
            
            # Extract key points for face tilt analysis
            # Left and right eye landmarks
            left_eye = face_landmarks.landmark[33]  # Left eye outer corner
            right_eye = face_landmarks.landmark[263]  # Right eye outer corner
            
            # Nose and chin landmarks
            nose_tip = face_landmarks.landmark[1]
            chin = face_landmarks.landmark[152]
            
            # Calculate image dimensions (needed for conversion to pixel coordinates)
            h, w = image_rgb.shape[:2]
            
            # Convert normalized coordinates to pixel coordinates
            left_eye_px = (int(left_eye.x * w), int(left_eye.y * h))
            right_eye_px = (int(right_eye.x * w), int(right_eye.y * h))
            nose_tip_px = (int(nose_tip.x * w), int(nose_tip.y * h))
            chin_px = (int(chin.x * w), int(chin.y * h))
            
            # Calculate eye midpoint
            eye_midpoint = (
                (left_eye_px[0] + right_eye_px[0]) // 2, 
                (left_eye_px[1] + right_eye_px[1]) // 2
            )
            
            # Calculate the angle between face vertical line and perpendicular axis
            dx = chin_px[0] - eye_midpoint[0]
            dy = chin_px[1] - eye_midpoint[1]
            
            # Calculate angle with perpendicular axis
            if dx == 0:  # Perfectly aligned with perpendicular
                face_tilt_angle = 0
            else:
                # Calculate angle in radians and convert to degrees
                face_tilt_angle = math.degrees(math.atan2(dx, dy))
            
            # Normalize to 0-90 degrees
            face_tilt_angle = abs(face_tilt_angle)
            if face_tilt_angle > 90:
                face_tilt_angle = 180 - face_tilt_angle
            
            # Determine tilt direction
            if chin_px[0] > eye_midpoint[0]:
                tilt_direction = "right"
            elif chin_px[0] < eye_midpoint[0]:
                tilt_direction = "left"
            else:
                tilt_direction = "none"
            
            # Determine face tilt status
            if face_tilt_angle < self.tilt_threshold:
                face_tilt_status = "Upright"
            else:
                face_tilt_status = f"Tilted {tilt_direction} by {face_tilt_angle:.2f} degrees"
            
            # Store landmarks
            landmarks_dict = {
                "left_eye": left_eye_px,
                "right_eye": right_eye_px,
                "nose_tip": nose_tip_px,
                "chin": chin_px,
                "eye_midpoint": eye_midpoint
            }
            
            # Create analysis result
            result = AnalysisResult(
                status=face_tilt_status,
                angle=face_tilt_angle,
                direction=tilt_direction,
                landmarks=landmarks_dict
            )
            
            return result
    
    def process_video(self, video_path: str, target_fps: float = None, show_progress: bool = True) -> VideoAnalysisStats:
        """
        Process video and analyze face tilt frame by frame, only collecting statistics
        
        Args:
            video_path: Path to the video file
            target_fps: Target frames per second to analyze (None = use video's native FPS)
            show_progress: Whether to display a progress bar during processing
            
        Returns:
            VideoAnalysisStats: Statistical summary of analysis
        """
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Error: Could not open video at {video_path}")
        
        # Get video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / video_fps if video_fps > 0 else 0
        
        # Calculate sampling rate based on target_fps
        if target_fps is None:
            # Use all frames (sampling rate of 1)
            sampling_rate = 1
            effective_fps = video_fps
        else:
            # Ensure target_fps doesn't exceed video's actual FPS
            effective_fps = min(target_fps, video_fps)
            
            # Calculate the sampling rate (how many frames to skip)
            # If video is 30fps and we want 5fps, we process every 6th frame
            sampling_rate = max(1, int(round(video_fps / effective_fps)))
        
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
                
            # Process every Nth frame based on calculated sampling rate
            if frame_index % sampling_rate == 0:
                # Process the frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self._analyze_frame(frame_rgb)
                
                if result is not None:
                    frames_with_detection += 1
                    angles.append(result.angle)
                    directions.append(result.direction)
                    timestamps.append(frame_index / video_fps)
                    
                    # Set frame metadata
                    result.frame_number = frame_index
                    result.timestamp = frame_index / video_fps
                    
                    frame_results.append({
                        "frame": frame_index,
                        "timestamp": frame_index / video_fps,
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
            print(f"\nFace Tilt Analysis Complete for {video_path}")
            print(f"- Duration: {duration:.2f} seconds")
            print(f"- Video FPS: {video_fps:.2f}, Target FPS: {effective_fps:.2f} (sampling rate: 1/{sampling_rate})")
            print(f"- Frames processed: {frames_with_detection}/{frame_index} ({detection_rate:.2f}%)")
            print(f"- Average tilt angle: {mean_angle:.2f}° ± {std_dev_angle:.2f}°")
            print(f"- Dominant tilt direction: {dominant_direction}")
            print(f"- Stability score: {stability_score:.2f} (lower is more stable)")
            print(f"- Processing time: {processing_time:.2f} seconds ({processing_fps:.2f} FPS)")
            
            return stats
        else:
            print("No valid face detection in video frames. Unable to generate statistics.")
            return None