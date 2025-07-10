import cv2
import math
import numpy as np
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import mediapipe as mp

@dataclass
class AnalysisResult:
    """Data class to store results of a single frame analysis."""
    status: str
    angle: float                   # Here, we continue using 'angle' to store motion distance (pixels)
    direction: str                 # 'excessive' or 'normal' based on z-score threshold
    landmarks: Dict = field(default_factory=dict)
    frame_number: Optional[int] = None
    timestamp: Optional[float] = None
    additional_info: Dict = field(default_factory=dict)

@dataclass
class VideoAnalysisStats:
    """Data class to store statistical results of video analysis."""
    mean_angle: float              # Mean motion distance (pixels)
    median_angle: float
    std_dev_angle: float
    min_angle: float
    max_angle: float
    dominant_direction: str        # "excessive" if many frames have high z-score, else "normal"
    direction_percentages: Dict[str, float]
    stability_score: float         # Here, we use std_dev as a measure of stability
    frames_analyzed: int
    frames_with_detection: int
    detection_rate: float
    duration_seconds: float
    movement_score: float          # Composite score (0-100) for overall hand movement
    excessive_motion_rate: float   # Percentage of frames with excessive movement
    avg_hands_per_frame: float
    processing_time: float
    processing_fps: float

class HandMotionAnalyzer:
    """Analyzer for hand movement during presentations using normalized metrics (z-score)."""
    
    def __init__(self, min_detection_confidence: float = 0.7, zscore_threshold: float = 2.0):
        """
        Args:
            min_detection_confidence: Confidence threshold for MediaPipe hands.
            zscore_threshold: Z-score value above which hand movement is flagged as 'excessive'.
        """
        self.min_detection_confidence = min_detection_confidence
        self.zscore_threshold = zscore_threshold  # Relative threshold in terms of standard deviations
        self.mp_hands = mp.solutions.hands
        self.prev_hand_positions = None  # To store hand positions from the previous frame
    
    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[AnalysisResult]:
        """Analyze a single frame to compute hand motion distance."""
        with self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=self.min_detection_confidence
        ) as hands:
            results = hands.process(image_rgb)
            if not results.multi_hand_landmarks:
                return None

            h, w = image_rgb.shape[:2]
            current_hand_positions = []
            hand_landmarks_dict = {}
            
            # Loop over detected hands
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Use wrist as reference position
                wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST.value]
                wrist_px = (int(wrist.x * w), int(wrist.y * h))
                
                # Calculate center of hand (average of all landmark coordinates)
                hand_x_sum = 0
                hand_y_sum = 0
                for landmark in hand_landmarks.landmark:
                    hand_x_sum += landmark.x
                    hand_y_sum += landmark.y
                hand_center = (
                    int((hand_x_sum / len(hand_landmarks.landmark)) * w),
                    int((hand_y_sum / len(hand_landmarks.landmark)) * h)
                )
                
                current_hand_positions.append(hand_center)
                hand_landmarks_dict[f"hand_{hand_idx}_wrist"] = wrist_px
                hand_landmarks_dict[f"hand_{hand_idx}_center"] = hand_center
                # Save all landmarks for visualization if needed
                for i, landmark in enumerate(hand_landmarks.landmark):
                    landmark_px = (int(landmark.x * w), int(landmark.y * h))
                    hand_landmarks_dict[f"hand_{hand_idx}_landmark_{i}"] = landmark_px

            # Compute motion distance between previous and current positions
            motion_distance = 0
            if self.prev_hand_positions is not None and len(self.prev_hand_positions) > 0:
                total_distance = 0
                valid_pairs = 0
                # For each current hand, find the closest previous hand position
                for curr_pos in current_hand_positions:
                    distances = [np.sqrt((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)
                                 for prev_pos in self.prev_hand_positions]
                    closest_distance = min(distances) if distances else 0
                    # Only use pairs that are reasonably close (avoid mismatches)
                    if closest_distance < w / 2:
                        total_distance += closest_distance
                        valid_pairs += 1
                if valid_pairs > 0:
                    motion_distance = total_distance / valid_pairs
            
            # Update previous hand positions for next frame
            self.prev_hand_positions = current_hand_positions
            
            # For compatibility, we use the field 'angle' to store motion distance.
            # We leave 'direction' empty here; it will be set later after z-score normalization.
            result = AnalysisResult(
                status="Hand motion detected",
                angle=motion_distance,
                direction="",
                landmarks=hand_landmarks_dict
            )
            return result

    def process_video(self, video_path: str, target_fps: Optional[float] = None, show_progress: bool = True) -> VideoAnalysisStats:
        """
        Process video frame by frame and analyze hand movements using a normalized z-score metric.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Error: Could not open video at {video_path}")
        
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / original_fps if original_fps > 0 else 0
        
        # Determine processing FPS and calculate frame interval for skipping
        processing_fps = original_fps if target_fps is None else target_fps
        frame_interval = 1 if processing_fps >= original_fps else int(original_fps / processing_fps)
        
        motion_distances = []
        timestamps = []
        frames_with_detection = 0
        frame_results = []
        hand_count_per_frame = []
        excessive_frames_flag = []  # To record whether each frame is excessive
        
        start_time = time.time()
        self.prev_hand_positions = None  # Reset previous hand positions
        
        frame_index = 0
        if show_progress:
            try:
                from tqdm import tqdm
                pbar = tqdm(total=frame_count, desc="Processing video")
            except ImportError:
                show_progress = False
                print("tqdm not installed, progress bar disabled")
        
        # First pass: Collect motion distances for each processed frame.
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_index % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self._analyze_frame(frame_rgb)
                if result is not None:
                    frames_with_detection += 1
                    motion_distance = result.angle
                    motion_distances.append(motion_distance)
                    timestamps.append(frame_index / original_fps)
                    
                    # Count detected hands from landmarks (using the 'center' key)
                    unique_hands = set(key.split('_')[1] for key in result.landmarks.keys() if key.startswith('hand_') and 'center' in key)
                    hand_count = len(unique_hands)
                    hand_count_per_frame.append(hand_count)
                    
                    # Store preliminary frame result (z-score evaluation will follow)
                    frame_results.append({
                        "frame": frame_index,
                        "timestamp": frame_index / original_fps,
                        "motion_distance": motion_distance,
                        "hands_detected": hand_count,
                        "status": result.status
                    })
            frame_index += 1
            if show_progress:
                pbar.update(1)
        if show_progress:
            pbar.close()
        
        processing_time = time.time() - start_time
        effective_fps = frame_count / processing_time
        
        cap.release()
        
        # If no motion data was collected, return early.
        if not motion_distances:
            print("No valid hand detection in video frames. Unable to generate statistics.")
            return None
        
        # Second pass: Compute overall statistics and z-scores.
        mean_motion = np.mean(motion_distances)
        std_dev_motion = np.std(motion_distances)
        median_motion = np.median(motion_distances)
        max_motion = np.max(motion_distances)
        
        # Compute z-scores for each frame's motion distance.
        # Note: if std_dev_motion is zero (e.g. no movement variation), set all z-scores to zero.
        z_scores = [(md - mean_motion) / std_dev_motion if std_dev_motion > 0 else 0 for md in motion_distances]
        
        # Flag frames with excessive movement based on z-score threshold.
        excessive_motion_frames = 0
        for z in z_scores:
            if z > self.zscore_threshold:
                excessive_motion_frames += 1
                excessive_frames_flag.append(True)
            else:
                excessive_frames_flag.append(False)
        
        # Define 'direction' for each frame result based on the z-score.
        # (We update the frame_results list with the z-score info if desired.)
        for idx, res in enumerate(frame_results):
            res["z_score"] = z_scores[idx]
            res["excessive_motion"] = "excessive" if z_scores[idx] > self.zscore_threshold else "normal"
        
        # Calculate overall excessive motion rate (percentage of frames with high z-score)
        excessive_motion_rate = (excessive_motion_frames / frames_with_detection) * 100 if frames_with_detection > 0 else 0
        
        # Average number of hands detected per frame
        avg_hands_per_frame = np.mean(hand_count_per_frame) if hand_count_per_frame else 0
        
        # Detection rate based on expected processed frames
        frames_expected = frame_count // frame_interval
        detection_rate = frames_with_detection / frames_expected * 100
        
        # Composite movement score: scale the mean motion relative to baseline;
        # you can adjust the scaling factor as needed (here we use 50 as a rough factor).
        movement_score = min(100, (mean_motion / (mean_motion + std_dev_motion + 1e-5)) * 50)
        
        # For 'dominant_direction' and percentages, we consider if most frames were flagged as excessive.
        dominant_direction = "excessive" if excessive_motion_rate > 50 else "normal"
        direction_percentages = {"excessive": excessive_motion_rate, "normal": 100 - excessive_motion_rate}
        
        stats = VideoAnalysisStats(
            mean_angle=mean_motion,
            median_angle=median_motion,
            std_dev_angle=std_dev_motion,
            min_angle=0,
            max_angle=max_motion,
            dominant_direction=dominant_direction,
            direction_percentages=direction_percentages,
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
        
        # Print a summary of the analysis
        print(f"\nHand Movement Analysis Complete for {video_path}")
        print(f"- Duration: {duration:.2f} seconds")
        print(f"- Original video FPS: {original_fps:.2f}")
        print(f"- Target processing FPS: {processing_fps:.2f}")
        print(f"- Frames processed: {frames_with_detection}/{frames_expected} ({detection_rate:.2f}%)")
        print(f"- Average hand movement: {mean_motion:.2f} pixels per frame")
        print(f"- Std. Dev. of movement: {std_dev_motion:.2f}")
        print(f"- Excessive movement flagged in {excessive_motion_frames} frames ({excessive_motion_rate:.2f}%)")
        print(f"- Movement score: {movement_score:.2f}/100")
        print(f"- Average hands detected per frame: {avg_hands_per_frame:.2f}")
        print(f"- Processing time: {processing_time:.2f} seconds ({effective_fps:.2f} FPS)")
        
        return stats