import cv2
import math
import numpy as np
import time
from typing import Dict, Optional
from dataclasses import dataclass
import mediapipe as mp

# Data class for single-frame rotation analysis
@dataclass
class RotationAnalysisResult:
    rotation_angle: float  # in degrees
    rotation_direction: str  # "clockwise", "anticlockwise", or "none"
    shoulder_distance: float
    landmarks: Dict
    frame_number: int = None
    timestamp: float = None

# Data class for video-level rotation statistics
@dataclass
class VideoRotationStats:
    mean_rotation_angle: float
    median_rotation_angle: float
    std_dev_rotation_angle: float
    min_rotation_angle: float
    max_rotation_angle: float
    dominant_rotation_direction: str
    rotation_direction_percentages: Dict[str, float]
    frames_analyzed: int
    frames_with_detection: int
    detection_rate: float
    duration_seconds: float

# Analyzer for body rotation relative to the camera (inferred from shoulder width)
class BodyRotationAnalyzer:
    def __init__(self, min_detection_confidence: float = 0.7):
        self.min_detection_confidence = min_detection_confidence
        self.mp_pose = mp.solutions.pose

    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[RotationAnalysisResult]:
        with self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=self.min_detection_confidence
        ) as pose:
            results = pose.process(image_rgb)
            if not results.pose_landmarks:
                return None

            landmarks = results.pose_landmarks.landmark
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

            h, w = image_rgb.shape[:2]
            left_shoulder_px = (int(left_shoulder.x * w), int(left_shoulder.y * h))
            right_shoulder_px = (int(right_shoulder.x * w), int(right_shoulder.y * h))
            
            # Calculate Euclidean distance between shoulders (as a proxy for frontal view)
            shoulder_distance = math.hypot(right_shoulder_px[0] - left_shoulder_px[0],
                                           right_shoulder_px[1] - left_shoulder_px[1])
            # Store landmarks and additional info
            landmarks_dict = {
                "left_shoulder": left_shoulder_px,
                "right_shoulder": right_shoulder_px
            }
            
            # For rotation direction, compare z-values:
            # If left_shoulder.z > right_shoulder.z, left shoulder is further away => rotation to right (clockwise)
            if left_shoulder.z > right_shoulder.z:
                rotation_direction = "clockwise"
            elif left_shoulder.z < right_shoulder.z:
                rotation_direction = "anticlockwise"
            else:
                rotation_direction = "none"

            # Initially, we cannot compute the rotation angle without a reference.
            # We'll return the measured shoulder_distance along with a placeholder angle of 0.
            result = RotationAnalysisResult(
                rotation_angle=0.0,  # to be updated later using a reference maximum distance
                rotation_direction=rotation_direction,
                shoulder_distance=shoulder_distance,
                landmarks=landmarks_dict
            )
            return result

    def process_video(self, video_path: str, target_fps: float = None, show_progress: bool = True) -> VideoRotationStats:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Error: Could not open video at {video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / video_fps if video_fps > 0 else 0

        if target_fps is None:
            sampling_rate = 1
            effective_fps = video_fps
        else:
            effective_fps = min(target_fps, video_fps)
            sampling_rate = max(1, int(round(video_fps / effective_fps)))

        # We will collect shoulder distances for all frames to determine the max (assumed frontal view)
        shoulder_distances = []
        rotation_angles = []
        rotation_directions = []
        frames_with_detection = 0
        frame_index = 0
        results_list = []
        start_time = time.time()

        if show_progress:
            try:
                from tqdm import tqdm
                pbar = tqdm(total=frame_count, desc="Processing video (rotation)")
            except ImportError:
                show_progress = False
                print("tqdm not installed, progress bar disabled")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_index % sampling_rate == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self._analyze_frame(frame_rgb)
                if result is not None:
                    frames_with_detection += 1
                    shoulder_distances.append(result.shoulder_distance)
                    # Temporarily store result; we'll compute rotation angle later once we have max distance
                    result.frame_number = frame_index
                    result.timestamp = frame_index / video_fps
                    results_list.append(result)
                    rotation_directions.append(result.rotation_direction)
            frame_index += 1
            if show_progress:
                pbar.update(1)
        if show_progress:
            pbar.close()
        processing_time = time.time() - start_time
        cap.release()

        if not shoulder_distances:
            print("No valid detection in video frames for rotation analysis.")
            return None

        # Use the maximum measured shoulder distance as the reference for a frontal view.
        max_shoulder_distance = max(shoulder_distances)

        # Now, update each result with an estimated rotation angle.
        # Assuming a simple perspective model: rotation_angle = arccos(current_distance / max_distance)
        for res in results_list:
            ratio = res.shoulder_distance / max_shoulder_distance
            # Ensure the ratio is within [0, 1]
            ratio = max(0.0, min(1.0, ratio))
            res.rotation_angle = math.degrees(math.acos(ratio))
            rotation_angles.append(res.rotation_angle)

        mean_rotation_angle = np.mean(rotation_angles)
        median_rotation_angle = np.median(rotation_angles)
        std_dev_rotation_angle = np.std(rotation_angles)
        min_rotation_angle = np.min(rotation_angles)
        max_rotation_angle = np.max(rotation_angles)
        direction_counts = {d: rotation_directions.count(d) for d in set(rotation_directions)}
        total_dirs = len(rotation_directions)
        rotation_direction_percentages = {d: (count / total_dirs) * 100 for d, count in direction_counts.items()}
        dominant_rotation_direction = max(direction_counts, key=direction_counts.get)
        detection_rate = frames_with_detection / (frame_count / sampling_rate) * 100

        print(f"\nRotation Analysis Complete for {video_path}")
        print(f"- Duration: {duration:.2f} seconds")
        print(f"- Video FPS: {video_fps:.2f}, Target FPS: {effective_fps:.2f} (sampling rate: 1/{sampling_rate})")
        print(f"- Frames processed: {frames_with_detection}/{frame_index} ({detection_rate:.2f}%)")
        print(f"- Average rotation angle: {mean_rotation_angle:.2f}° ± {std_dev_rotation_angle:.2f}°")
        print(f"- Dominant rotation direction: {dominant_rotation_direction}")
        print(f"- Processing time: {processing_time:.2f} seconds")
        
        return VideoRotationStats(
            mean_rotation_angle=mean_rotation_angle,
            median_rotation_angle=median_rotation_angle,
            std_dev_rotation_angle=std_dev_rotation_angle,
            min_rotation_angle=min_rotation_angle,
            max_rotation_angle=max_rotation_angle,
            dominant_rotation_direction=dominant_rotation_direction,
            rotation_direction_percentages=rotation_direction_percentages,
            frames_analyzed=frame_index,
            frames_with_detection=frames_with_detection,
            detection_rate=detection_rate,
            duration_seconds=duration
        )
