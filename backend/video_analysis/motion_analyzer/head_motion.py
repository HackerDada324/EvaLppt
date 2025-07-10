import cv2
import math
import numpy as np
import time
from typing import Dict, Optional
from dataclasses import dataclass
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

class HeadTiltAnalyzer:
    """Analyzer for head tilt using MediaPipe Face Mesh"""
    
    def __init__(self, min_detection_confidence: float = 0.5, tilt_threshold: float = 5):
        self.min_detection_confidence = min_detection_confidence
        self.tilt_threshold = tilt_threshold
        self.mp_face_mesh = mp.solutions.face_mesh
    
    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[AnalysisResult]:
        """Analyze a single frame for head tilt statistics only"""
        # Initialize Face Mesh (using static image mode)
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
            
            # Extract key landmarks
            left_eye = face_landmarks.landmark[33]  # Left eye outer corner
            right_eye = face_landmarks.landmark[263]  # Right eye outer corner
            nose_tip = face_landmarks.landmark[1]
            chin = face_landmarks.landmark[152]
            
            # Get image dimensions
            h, w = image_rgb.shape[:2]
            
            # Convert normalized coordinates to pixel coordinates
            left_eye_px = (int(left_eye.x * w), int(left_eye.y * h))
            right_eye_px = (int(right_eye.x * w), int(right_eye.y * h))
            nose_tip_px = (int(nose_tip.x * w), int(nose_tip.y * h))
            chin_px = (int(chin.x * w), int(chin.y * h))
            
            # Calculate the midpoint between eyes
            eye_midpoint = ((left_eye_px[0] + right_eye_px[0]) // 2,
                            (left_eye_px[1] + right_eye_px[1]) // 2)
            
            # Compute differences
            dx = chin_px[0] - eye_midpoint[0]
            dy = chin_px[1] - eye_midpoint[1]
            
            # Calculate tilt angle (angle between vertical and the line from eye midpoint to chin)
            if dx == 0:
                face_tilt_angle = 0
            else:
                face_tilt_angle = math.degrees(math.atan2(dx, dy))
            
            # Normalize angle (0-90°)
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
            
            # Status message
            if face_tilt_angle < self.tilt_threshold:
                face_tilt_status = "Upright"
            else:
                face_tilt_status = f"Tilted {tilt_direction} by {face_tilt_angle:.2f}°"
            
            landmarks_dict = {
                "left_eye": left_eye_px,
                "right_eye": right_eye_px,
                "nose_tip": nose_tip_px,
                "chin": chin_px,
                "eye_midpoint": eye_midpoint
            }
            
            return AnalysisResult(
                status=face_tilt_status,
                angle=face_tilt_angle,
                direction=tilt_direction,
                landmarks=landmarks_dict
            )
    
    def process_video(self, video_path: str, target_fps: float = None, show_progress: bool = True) -> VideoAnalysisStats:
        """
        Process video and analyze face tilt frame by frame, only collecting statistics.
        """
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
                pbar = tqdm(total=frame_count, desc="Processing video")
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
            total = len(directions)
            direction_percentages = {d: (count / total) * 100 for d, count in direction_counts.items()}
            dominant_direction = max(direction_counts, key=direction_counts.get)
            stability_score = std_dev_angle
            detection_rate = frames_with_detection / (frame_count / sampling_rate) * 100
            
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
            
            print(f"\nFace Tilt Analysis Complete for {video_path}")
            print(f"- Duration: {duration:.2f} sec")
            print(f"- Video FPS: {video_fps:.2f}, Target FPS: {effective_fps:.2f} (sampling every {sampling_rate} frame(s))")
            print(f"- Frames with detection: {frames_with_detection}/{frame_index} ({detection_rate:.2f}%)")
            print(f"- Average tilt angle: {mean_angle:.2f}° ± {std_dev_angle:.2f}°")
            print(f"- Dominant tilt direction: {dominant_direction}")
            print(f"- Stability score: {stability_score:.2f}")
            print(f"- Processing time: {processing_time:.2f} sec")
            
            return stats
        else:
            print("No face detected in any frame.")
            return None