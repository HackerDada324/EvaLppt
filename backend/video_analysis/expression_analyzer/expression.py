import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, SiglipForImageClassification
from dataclasses import dataclass
from tqdm import tqdm

@dataclass
class EmotionAnalysisResult:
    emotion_scores: dict
    average_scores: dict

class FacialExpressionAnalyzer:
    def __init__(self, model_name: str = "prithivMLmods/Facial-Emotion-Detection-SigLIP2", use_gpu: bool = True):
        self.device = torch.device("cuda" if torch.cuda.is_available() and use_gpu else "cpu")
        self.processor = AutoImageProcessor.from_pretrained(model_name, use_fast=True)
        self.model = SiglipForImageClassification.from_pretrained(model_name).to(self.device)
        self.labels = {
            "0": "Ahegao", "1": "Angry", "2": "Happy", "3": "Neutral",
            "4": "Sad", "5": "Surprise"
        }

    def _analyze_frame(self, image_rgb: np.ndarray) -> dict:
        """Analyze a single frame and return emotion probabilities"""
        pil_image = Image.fromarray(image_rgb).convert("RGB")
        inputs = self.processor(images=pil_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=1).squeeze().tolist()
        
        return {self.labels[str(i)]: probs[i] for i in range(len(probs))}
    
    def process_video(self, video_path: str, target_fps: float = None, show_progress: bool = True) -> EmotionAnalysisResult:
        """
        Process video and calculate average scores for all emotions
        
        Args:
            video_path: Path to the video file
            target_fps: Target frames per second to analyze (None = use video's native FPS)
            show_progress: Whether to display a progress bar during processing
            
        Returns:
            EmotionAnalysisResult: Emotion analysis results including totals and averages
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
        emotion_totals = {emotion: 0.0 for emotion in self.labels.values()}
        analyzed_frames = 0
        frame_index = 0
        
        # Create progress bar if requested
        if show_progress:
            pbar = tqdm(total=frame_count, desc="Processing video")
        
        # Start processing
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process every Nth frame based on calculated sampling rate
            if frame_index % sampling_rate == 0:
                # Process the frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                scores = self._analyze_frame(frame_rgb)
                
                # Accumulate emotion scores
                for emotion, score in scores.items():
                    emotion_totals[emotion] += score
                
                analyzed_frames += 1
            
            frame_index += 1
            
            # Update progress bar
            if show_progress:
                pbar.update(1)
        
        # Close progress bar
        if show_progress:
            pbar.close()
            
        # Release resources
        cap.release()
        
        # Compute average emotion scores
        if analyzed_frames == 0:
            print("No frames were analyzed. Check if the video contains valid frames.")
            return EmotionAnalysisResult(emotion_scores={}, average_scores={})
        
        average_scores = {emotion: total / analyzed_frames for emotion, total in emotion_totals.items()}
        
        # Print summary
        print(f"\nFacial Expression Analysis Complete for {video_path}")
        print(f"- Duration: {duration:.2f} seconds")
        print(f"- Video FPS: {video_fps:.2f}, Target FPS: {effective_fps:.2f} (sampling rate: 1/{sampling_rate})")
        print(f"- Frames analyzed: {analyzed_frames}/{frame_index}")
        print("- Average emotion scores:")
        for emotion, score in sorted(average_scores.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {emotion}: {score:.2%}")
        
        return EmotionAnalysisResult(emotion_scores=emotion_totals, average_scores=average_scores)