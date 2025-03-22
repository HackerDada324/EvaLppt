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
    
    def process_video(self, video_path: str, sampling_rate: int = 1) -> EmotionAnalysisResult:
        """Process video and calculate average scores for all emotions"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Error: Could not open video at {video_path}")
        
        # Get total frame count for the progress bar
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        emotion_totals = {emotion: 0.0 for emotion in self.labels.values()}
        analyzed_frames = 0
        frame_count = 0
        
        # Create progress bar
        pbar = tqdm(total=total_frames, desc="Processing video")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sampling_rate == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                scores = self._analyze_frame(frame_rgb)
                for emotion, score in scores.items():
                    emotion_totals[emotion] += score
                analyzed_frames += 1
            
            frame_count += 1
            pbar.update(1)
        
        pbar.close()
        cap.release()
        
        # Compute average emotion scores
        if analyzed_frames == 0:
            return EmotionAnalysisResult(emotion_scores={}, average_scores={})
        
        average_scores = {emotion: total / analyzed_frames for emotion, total in emotion_totals.items()}
        return EmotionAnalysisResult(emotion_scores=emotion_totals, average_scores=average_scores)