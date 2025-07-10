import cv2
import math
import numpy as np
import time
from typing import Dict, Optional
from dataclasses import dataclass
import mediapipe as mp

@dataclass
class AnalysisResult:
    """Data class to store results of a single frame analysis."""
    status: str
    angle: float                   # Absolute pitch angle (in degrees)
    direction: str                 # "forward" (chin down) or "backward" (chin up) or "neutral"
    landmarks: Dict
    frame_number: Optional[int] = None
    timestamp: Optional[float] = None

@dataclass
class VideoAnalysisStats:
    """Data class to store statistical results of video analysis."""
    mean_angle: float              # Mean pitch angle (degrees)
    median_angle: float
    std_dev_angle: float
    min_angle: float
    max_angle: float
    dominant_direction: str        # "forward", "backward", or "neutral"
    direction_percentages: Dict[str, float]
    stability_score: float         # Here, we use std_dev as a measure of stability
    frames_analyzed: int
    frames_with_detection: int
    detection_rate: float
    duration_seconds: float

class HeadPitchAnalyzer:
    """Analyzer for head forward/backward (pitch) movement using MediaPipe Face Mesh and solvePnP."""
    
    def __init__(self, min_detection_confidence: float = 0.5, pitch_threshold: float = 5):
        """
        Args:
            min_detection_confidence: Minimum confidence for face detection.
            pitch_threshold: Threshold (in degrees) below which the head is considered 'neutral'.
        """
        self.min_detection_confidence = min_detection_confidence
        self.pitch_threshold = pitch_threshold
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # Define 3D model points for head pose estimation (in millimeters)
        # Using typical facial landmarks: nose tip, chin, left eye outer corner,
        # right eye outer corner, left mouth corner, right mouth corner.
        self.model_points = np.array([
            (0.0, 0.0, 0.0),          # Nose tip
            (0.0, -63.6, -12.5),      # Chin
            (-43.3, 32.7, -26.0),     # Left eye outer corner
            (43.3, 32.7, -26.0),      # Right eye outer corner
            (-28.9, -28.9, -24.1),    # Left mouth corner
            (28.9, -28.9, -24.1)      # Right mouth corner
        ], dtype="double")
        
        # Define indices for corresponding 2D landmarks from MediaPipe Face Mesh.
        self.landmark_indices = {
            "nose_tip": 1,
            "chin": 152,
            "left_eye": 33,      # left eye outer corner
            "right_eye": 263,    # right eye outer corner
            "left_mouth": 61,    # left mouth corner
            "right_mouth": 291   # right mouth corner
        }
    
    def _get_euler_angles(self, rotation_matrix: np.ndarray) -> tuple:
        """
        Convert rotation matrix to Euler angles (pitch, yaw, roll) in degrees.
        This implementation uses cv2.decomposeProjectionMatrix.
        """
        # Append a zero translation column to create a projection matrix for decomposition.
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(np.hstack((rotation_matrix, np.zeros((3,1)))))
        pitch = float(euler_angles[0])
        yaw = float(euler_angles[1])
        roll = float(euler_angles[2])
        return pitch, yaw, roll

    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[AnalysisResult]:
        """Analyze a single frame to estimate head pitch (forward/backward lean)."""
        # Initialize Face Mesh for the frame
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
            h, w = image_rgb.shape[:2]
            
            # Extract the required 2D image points from the detected landmarks.
            image_points = []
            landmarks_dict = {}
            for key, idx in self.landmark_indices.items():
                lm = face_landmarks.landmark[idx]
                coord = (int(lm.x * w), int(lm.y * h))
                image_points.append(coord)
                landmarks_dict[key] = coord
            image_points = np.array(image_points, dtype="double")
            
            # Define camera matrix using image dimensions.
            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype="double")
            dist_coeffs = np.zeros((4,1))  # Assuming no lens distortion
            
            # Solve the PnP problem to estimate head pose.
            success, rotation_vector, translation_vector = cv2.solvePnP(
                self.model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )
            if not success:
                return None
            
            # Convert rotation vector to rotation matrix.
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            # Extract Euler angles.
            pitch, yaw, roll = self._get_euler_angles(rotation_matrix)
            
            # For pitch, positive value often indicates head leaning forward (chin down),
            # while a negative value indicates head leaning backward (chin up).
            # We'll use the absolute pitch angle for reporting,
            # but keep the sign to determine the direction.
            abs_pitch = abs(pitch)
            if abs_pitch < self.pitch_threshold:
                pitch_status = "Neutral"
                pitch_direction = "neutral"
            else:
                if pitch > 0:
                    pitch_status = f"Leaning forward (chin down) by {abs_pitch:.2f}°"
                    pitch_direction = "forward"
                else:
                    pitch_status = f"Leaning backward (chin up) by {abs_pitch:.2f}°"
                    pitch_direction = "backward"
            
            return AnalysisResult(
                status=pitch_status,
                angle=abs_pitch,
                direction=pitch_direction,
                landmarks=landmarks_dict
            )
    
    def process_video(self, video_path: str, target_fps: Optional[float] = None, show_progress: bool = True) -> VideoAnalysisStats:
        """
        Process video and analyze head pitch (forward/backward lean) frame by frame.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Error: Could not open video at {video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / video_fps if video_fps > 0 else 0
        
        # Determine sampling rate for processing
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
            
            print(f"\nHead Pitch Analysis Complete for {video_path}")
            print(f"- Duration: {duration:.2f} sec")
            print(f"- Video FPS: {video_fps:.2f}, Target FPS: {effective_fps:.2f} (sampling every {sampling_rate} frame(s))")
            print(f"- Frames with detection: {frames_with_detection}/{frame_index} ({detection_rate:.2f}%)")
            print(f"- Average pitch angle: {mean_angle:.2f}° ± {std_dev_angle:.2f}°")
            print(f"- Dominant pitch direction: {dominant_direction}")
            print(f"- Stability score: {stability_score:.2f}")
            print(f"- Processing time: {processing_time:.2f} sec")
            
            return stats
        else:
            print("No face detected in any frame.")
            return None