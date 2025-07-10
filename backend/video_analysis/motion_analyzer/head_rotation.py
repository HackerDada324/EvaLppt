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
    yaw_angle: float
    landmarks: Dict
    frame_number: int = None
    timestamp: float = None

@dataclass
class VideoAnalysisStats:
    """Data class to store statistical results of video analysis"""
    mean_yaw: float
    median_yaw: float
    std_dev_yaw: float
    min_yaw: float
    max_yaw: float
    frames_analyzed: int
    frames_with_detection: int
    detection_rate: float
    duration_seconds: float

class HeadRotationAnalyzer:
    """Analyzer for head rotation (yaw) using MediaPipe Face Mesh and solvePnP"""
    
    def __init__(self, min_detection_confidence: float = 0.5):
        self.min_detection_confidence = min_detection_confidence
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # Define indices for key landmarks:
        # Nose tip, Chin, Left eye (outer corner), Right eye (outer corner),
        # Left mouth corner, Right mouth corner.
        self.landmark_indices = {
            "nose_tip": 1,
            "chin": 152,
            "left_eye": 33,
            "right_eye": 263,
            "left_mouth": 61,
            "right_mouth": 291
        }
        # 3D model points (in a canonical coordinate system, unit: millimeters)
        self.model_points = np.array([
            (0.0, 0.0, 0.0),          # Nose tip
            (0.0, -63.6, -12.5),      # Chin
            (-43.3, 32.7, -26.0),     # Left eye outer corner
            (43.3, 32.7, -26.0),      # Right eye outer corner
            (-28.9, -28.9, -24.1),    # Left mouth corner
            (28.9, -28.9, -24.1)      # Right mouth corner
        ], dtype="double")
    
    def _get_euler_angles(self, rotation_matrix: np.ndarray) -> tuple:
        """
        Convert a rotation matrix to Euler angles (pitch, yaw, roll)
        Using cv2.decomposeProjectionMatrix for simplicity.
        """
        # Append a column for projection decomposition
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(np.hstack((rotation_matrix, np.zeros((3,1)))))
        pitch = float(euler_angles[0])
        yaw = float(euler_angles[1])
        roll = float(euler_angles[2])
        return pitch, yaw, roll

    def _analyze_frame(self, image_rgb: np.ndarray) -> Optional[AnalysisResult]:
        """Analyze a single frame to detect head rotation (yaw)"""
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
            
            # Extract the 2D image points for our landmarks
            image_points = []
            landmarks_dict = {}
            for key, idx in self.landmark_indices.items():
                lm = face_landmarks.landmark[idx]
                coord = (int(lm.x * w), int(lm.y * h))
                image_points.append(coord)
                landmarks_dict[key] = coord
            image_points = np.array(image_points, dtype="double")
            
            # Define camera parameters: focal length based on image width, center at image center
            focal_length = w
            center = (w / 2, h / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype="double")
            
            dist_coeffs = np.zeros((4,1))  # Assuming no lens distortion
            
            # Solve the PnP problem to get rotation and translation vectors
            success, rotation_vector, translation_vector = cv2.solvePnP(
                self.model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
            )
            
            if not success:
                return None
            
            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            # Extract Euler angles (pitch, yaw, roll)
            pitch, yaw, roll = self._get_euler_angles(rotation_matrix)
            # We are interested in yaw (rotation around the vertical axis)
            yaw_angle = yaw  # in degrees
            
            # Create a status message
            status_msg = f"Head rotated with yaw = {yaw_angle:.2f}°"
            
            return AnalysisResult(
                status=status_msg,
                yaw_angle=yaw_angle,
                landmarks=landmarks_dict
            )
    
    def process_video(self, video_path: str, target_fps: float = None, show_progress: bool = True) -> VideoAnalysisStats:
        """
        Process video and analyze head rotation (yaw) frame by frame.
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
        
        yaw_angles = []
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
                    yaw_angles.append(result.yaw_angle)
            frame_index += 1
            if show_progress:
                pbar.update(1)
        
        if show_progress:
            pbar.close()
        processing_time = time.time() - start_time
        cap.release()
        
        if yaw_angles:
            mean_yaw = np.mean(yaw_angles)
            median_yaw = np.median(yaw_angles)
            std_dev_yaw = np.std(yaw_angles)
            min_yaw = np.min(yaw_angles)
            max_yaw = np.max(yaw_angles)
            detection_rate = frames_with_detection / (frame_count / sampling_rate) * 100
            
            stats = VideoAnalysisStats(
                mean_yaw=mean_yaw,
                median_yaw=median_yaw,
                std_dev_yaw=std_dev_yaw,
                min_yaw=min_yaw,
                max_yaw=max_yaw,
                frames_analyzed=frame_index,
                frames_with_detection=frames_with_detection,
                detection_rate=detection_rate,
                duration_seconds=duration
            )
            
            print(f"\nHead Rotation Analysis Complete for {video_path}")
            print(f"- Duration: {duration:.2f} sec")
            print(f"- Video FPS: {video_fps:.2f}, Target FPS: {effective_fps:.2f} (sampling every {sampling_rate} frame(s))")
            print(f"- Frames with detection: {frames_with_detection}/{frame_index} ({detection_rate:.2f}%)")
            print(f"- Average yaw angle: {mean_yaw:.2f}° ± {std_dev_yaw:.2f}°")
            print(f"- Min/Max yaw: {min_yaw:.2f}°/{max_yaw:.2f}°")
            print(f"- Processing time: {processing_time:.2f} sec")
            
            return stats
        else:
            print("No face detection for head rotation.")
            return None