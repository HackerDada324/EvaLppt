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
    landmarks: Dict = field(default_factory=dict)
    frame_number: Optional[int] = None
    timestamp: Optional[float] = None
    additional_info: Dict = field(default_factory=dict)

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
    movement_score: float = 0.0
    excessive_motion_rate: float = 0.0
    avg_hands_per_frame: float = 0.0
    processing_time: float = 0.0
    processing_fps: float = 0.0

class HandMotionAnalyzer:
    """Analyzer for hand movement during presentations, detecting excessive motion"""
    
    def __init__(self, min_detection_confidence: float = 0.7, motion_threshold: float = 30):
        self.min_detection_confidence = min_detection_confidence
        self.motion_threshold = motion_threshold 
        self.mp_hands = mp.solutions.hands
        self.prev_hand_positions = None  
    
    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[AnalysisResult]:
        """Analyze a single frame for hand movement statistics"""
        # Initialize Hands model
        with self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=self.min_detection_confidence
        ) as hands:
            results = hands.process(image_rgb)
            
            if not results.multi_hand_landmarks:
                return None
            
            # Get image dimensions
            h, w = image_rgb.shape[:2]
            
            # Track hand centers and movement
            current_hand_positions = []
            hand_landmarks_dict = {}
            
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Use wrist as the reference point for hand position
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST.value]
                wrist_px = (int(wrist.x * w), int(wrist.y * h))
                
                # Calculate center of hand (average of all landmarks)
                hand_x_sum = 0
                hand_y_sum = 0
                
                for landmark in hand_landmarks.landmark:
                    hand_x_sum += landmark.x
                    hand_y_sum += landmark.y
                
                hand_center = (
                    int((hand_x_sum / len(hand_landmarks.landmark)) * w),
                    int((hand_y_sum / len(hand_landmarks.landmark)) * h)
                )
                
                # Store hand position
                current_hand_positions.append(hand_center)
                
                # Store key hand landmarks for visualization
                hand_landmarks_dict[f"hand_{hand_idx}_wrist"] = wrist_px
                hand_landmarks_dict[f"hand_{hand_idx}_center"] = hand_center
                
                # Store all landmark points for this hand
                for i, landmark in enumerate(hand_landmarks.landmark):
                    landmark_px = (int(landmark.x * w), int(landmark.y * h))
                    hand_landmarks_dict[f"hand_{hand_idx}_landmark_{i}"] = landmark_px
            
            # Calculate motion metrics
            motion_distance = 0
            motion_speed = 0
            excessive_motion = False
            
            if self.prev_hand_positions is not None and len(self.prev_hand_positions) > 0:
                # Calculate total movement distance for all detected hands
                total_distance = 0
                valid_hand_pairs = 0
                
                # Match hands between frames based on proximity
                for curr_pos in current_hand_positions:
                    # Find the closest previous hand position
                    if len(self.prev_hand_positions) > 0:
                        distances = [np.sqrt((curr_pos[0] - prev_pos[0])**2 + 
                                             (curr_pos[1] - prev_pos[1])**2) 
                                    for prev_pos in self.prev_hand_positions]
                        closest_idx = np.argmin(distances)
                        
                        # Only consider if reasonably close (prevents mismatching completely different hands)
                        if distances[closest_idx] < w/2:  # Half the frame width as threshold
                            total_distance += distances[closest_idx]
                            valid_hand_pairs += 1
                
                if valid_hand_pairs > 0:
                    motion_distance = total_distance / valid_hand_pairs
                    # Determine if motion is excessive based on threshold
                    excessive_motion = motion_distance > self.motion_threshold
            
            # Update previous hand positions for next frame
            self.prev_hand_positions = current_hand_positions
            
            # Determine movement status and angle (for compatibility with AnalysisResult)
            if not current_hand_positions:
                movement_status = "No hands detected"
            elif excessive_motion:
                movement_status = f"Excessive hand movement: {motion_distance:.2f} pixels"
            else:
                movement_status = f"Normal hand movement: {motion_distance:.2f} pixels"
            
            # Store motion data in status/angle/direction fields for compatibility
            # We'll use angle to store the motion distance
            motion_angle = motion_distance  
            
            # Use direction to store excessive motion status
            motion_direction = "excessive" if excessive_motion else "normal"
            
            # Create analysis result using only the fields that exist in your class
            result = AnalysisResult(
                status=movement_status,
                angle=motion_angle,  # Using angle to store motion distance
                direction=motion_direction,  # Using direction to store motion status
                landmarks=hand_landmarks_dict
            )
            
            return result
    
    def process_video(self, video_path: str, target_fps: Optional[float] = None, show_progress: bool = True) -> VideoAnalysisStats:
        """
        Process video and analyze hand movements frame by frame
        
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
        motion_distances = []
        excessive_motion_frames = 0
        timestamps = []
        frames_with_detection = 0
        frame_results = []
        hand_count_per_frame = []
        
        # Start timing
        start_time = time.time()
        
        # Reset previous hand positions
        self.prev_hand_positions = None
        
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
                    
                    # We're using angle to store motion distance
                    motion_distance = result.angle
                    motion_distances.append(motion_distance)
                    
                    # We're using direction to store motion status
                    if result.direction == "excessive":
                        excessive_motion_frames += 1
                    
                    # Count hands from landmarks dict
                    unique_hands = set([key.split('_')[1] for key in result.landmarks.keys() 
                                    if key.startswith('hand_') and 'center' in key])
                    hand_count = len(unique_hands)
                    hand_count_per_frame.append(hand_count)
                    
                    timestamps.append(frame_index / original_fps)
                    
                    # Set frame metadata
                    result.frame_number = frame_index
                    result.timestamp = frame_index / original_fps
                    
                    # Store frame results
                    frame_results.append({
                        "frame": frame_index,
                        "timestamp": frame_index / original_fps,
                        "motion_distance": motion_distance,
                        "excessive_motion": (result.direction == "excessive"),
                        "hands_detected": hand_count,
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
        if motion_distances:
            # Basic statistics
            mean_motion = np.mean(motion_distances)
            median_motion = np.median(motion_distances)
            std_dev_motion = np.std(motion_distances)
            max_motion = np.max(motion_distances)
            
            # Calculate excessive motion percentage
            excessive_motion_rate = (excessive_motion_frames / frames_with_detection) * 100 if frames_with_detection > 0 else 0
            
            # Calculate average hands per frame
            avg_hands_per_frame = np.mean(hand_count_per_frame) if hand_count_per_frame else 0
            
            # Calculate detection rate
            frames_expected = frame_count // frame_interval
            detection_rate = frames_with_detection / frames_expected * 100
            
            # Calculate a hand movement score (0-100, higher means more movement)
            movement_score = min(100, (mean_motion / self.motion_threshold) * 50)

            stats = VideoAnalysisStats(
                mean_angle=mean_motion,
                median_angle=median_motion,
                std_dev_angle=std_dev_motion,
                min_angle=0,
                max_angle=max_motion,
                dominant_direction="excessive" if excessive_motion_rate > 50 else "normal",
                direction_percentages={"excessive": excessive_motion_rate, "normal": 100 - excessive_motion_rate},
                stability_score=std_dev_motion,
                frames_analyzed=frame_index,
                frames_with_detection=frames_with_detection,
                detection_rate=detection_rate,
                duration_seconds=duration,
                movement_score=movement_score,
                excessive_motion_rate=excessive_motion_rate,
                avg_hands_per_frame=avg_hands_per_frame,
                processing_time=processing_time,
                processing_fps=effective_fps
            )
            
            # Print summary
            print(f"\nHand Movement Analysis Complete for {video_path}")
            print(f"- Duration: {duration:.2f} seconds")
            print(f"- Original video FPS: {original_fps:.2f}")
            print(f"- Target processing FPS: {processing_fps:.2f}")
            print(f"- Frames processed: {frames_with_detection}/{frames_expected} ({detection_rate:.2f}%)")
            print(f"- Average hand movement: {mean_motion:.2f} pixels per frame")
            print(f"- Excessive movement detected in {excessive_motion_frames} frames ({excessive_motion_rate:.2f}%)")
            print(f"- Movement score: {movement_score:.2f}/100")
            print(f"- Average hands detected per frame: {avg_hands_per_frame:.2f}")
            print(f"- Processing time: {processing_time:.2f} seconds ({effective_fps:.2f} FPS)")
            
            return stats
        else:
            print("No valid hand detection in video frames. Unable to generate statistics.")
            return None