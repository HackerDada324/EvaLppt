import cv2
import math
import numpy as np
import time
from typing import Dict, Optional
from dataclasses import dataclass
import mediapipe as mp

# Data class for single-frame tilt analysis
@dataclass
class TiltAnalysisResult:
    status: str
    angle: float
    direction: str  # "left", "right", or "none"
    landmarks: Dict
    frame_number: int = None
    timestamp: float = None

# Data class for video-level tilt statistics
@dataclass
class VideoTiltStats:
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

# Analyzer for body tilt (spine alignment relative to vertical axis)
class BodyTiltAnalyzer:
    def __init__(self, min_detection_confidence: float = 0.7, tilt_threshold: float = 5):
        self.min_detection_confidence = min_detection_confidence
        self.tilt_threshold = tilt_threshold
        self.mp_pose = mp.solutions.pose

    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[TiltAnalysisResult]:
        with self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=self.min_detection_confidence
        ) as pose:
            results = pose.process(image_rgb)
            if not results.pose_landmarks:
                return None

            landmarks = results.pose_landmarks.landmark

            # Get key landmarks: shoulders and hips
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]

            # Convert normalized coordinates to pixel coordinates
            h, w = image_rgb.shape[:2]
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

            # Calculate angle between the spine (line joining midpoints) and the vertical axis.
            dx = shoulder_midpoint[0] - hip_midpoint[0]
            dy = shoulder_midpoint[1] - hip_midpoint[1]
            if dx == 0:
                spine_angle = 0
            else:
                spine_angle = math.degrees(math.atan2(dx, dy))
            spine_angle = abs(spine_angle)
            if spine_angle > 90:
                spine_angle = 180 - spine_angle

            # Determine tilt direction based on horizontal shift of shoulders vs. hips.
            if shoulder_midpoint[0] > hip_midpoint[0]:
                tilt_direction = "right"
            elif shoulder_midpoint[0] < hip_midpoint[0]:
                tilt_direction = "left"
            else:
                tilt_direction = "none"

            if spine_angle < self.tilt_threshold:
                alignment_status = "Vertical"
            else:
                alignment_status = f"Tilted {tilt_direction} by {spine_angle:.2f}°"

            landmarks_dict = {
                "left_shoulder": left_shoulder_px,
                "right_shoulder": right_shoulder_px,
                "left_hip": left_hip_px,
                "right_hip": right_hip_px,
                "shoulder_midpoint": shoulder_midpoint,
                "hip_midpoint": hip_midpoint
            }

            result = TiltAnalysisResult(
                status=alignment_status,
                angle=spine_angle,
                direction=tilt_direction,
                landmarks=landmarks_dict
            )
            return result

    def process_video(self, video_path: str, target_fps: float = None, show_progress: bool = True) -> VideoTiltStats:
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

        angles = []
        directions = []
        frames_with_detection = 0
        frame_index = 0
        start_time = time.time()

        if show_progress:
            try:
                from tqdm import tqdm
                pbar = tqdm(total=frame_count, desc="Processing video (tilt)")
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
                    angles.append(result.angle)
                    directions.append(result.direction)
                    result.frame_number = frame_index
                    result.timestamp = frame_index / video_fps

            frame_index += 1
            if show_progress:
                pbar.update(1)
        if show_progress:
            pbar.close()
        processing_time = time.time() - start_time
        cap.release()

        if angles:
            mean_angle = np.mean(angles)
            median_angle = np.median(angles)
            std_dev_angle = np.std(angles)
            min_angle = np.min(angles)
            max_angle = np.max(angles)
            direction_counts = {d: directions.count(d) for d in set(directions)}
            total_dirs = len(directions)
            direction_percentages = {d: (count / total_dirs) * 100 for d, count in direction_counts.items()}
            dominant_direction = max(direction_counts, key=direction_counts.get)
            stability_score = std_dev_angle
            detection_rate = frames_with_detection / (frame_count / sampling_rate) * 100

            print(f"\nTilt Analysis Complete for {video_path}")
            print(f"- Duration: {duration:.2f} seconds")
            print(f"- Video FPS: {video_fps:.2f}, Target FPS: {effective_fps:.2f} (sampling rate: 1/{sampling_rate})")
            print(f"- Frames processed: {frames_with_detection}/{frame_index} ({detection_rate:.2f}%)")
            print(f"- Average tilt angle: {mean_angle:.2f}° ± {std_dev_angle:.2f}°")
            print(f"- Dominant tilt direction: {dominant_direction}")
            print(f"- Stability score: {stability_score:.2f} (lower is more stable)")
            print(f"- Processing time: {processing_time:.2f} seconds")
            
            return VideoTiltStats(
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
        else:
            print("No valid detection in video frames for tilt analysis.")
            return None