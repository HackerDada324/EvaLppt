"""
Audio processing utilities for the Auto PPT Evaluation System
"""
import os
from typing import Optional

from .exceptions import ProcessingError


class AudioProcessor:
    """Handles audio extraction and transcription operations"""
    
    def __init__(self, whisper_model=None):
        """
        Initialize audio processor
        
        Args:
            whisper_model: Pre-loaded Whisper model for transcription
        """
        self.whisper_model = whisper_model
        
        # Check for moviepy availability
        try:
            import moviepy.editor as mp
            self.moviepy = mp
            self.moviepy_available = True
        except ImportError:
            self.moviepy = None
            self.moviepy_available = False
    
    def extract_audio_from_video(self, video_path: str, audio_path: str) -> bool:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to the video file
            audio_path: Path where audio should be saved
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ProcessingError: If audio extraction fails
        """
        if not self.moviepy_available:
            raise ProcessingError("MoviePy not available for audio extraction")
        
        if not os.path.exists(video_path):
            raise ProcessingError(f"Video file not found: {video_path}")
        
        try:
            video = self.moviepy.VideoFileClip(video_path)
            audio = video.audio
            
            if audio is None:
                raise ProcessingError("No audio track found in video")
            
            # Write audio file without verbose output
            audio.write_audiofile(audio_path, verbose=False, logger=None)
            
            # Clean up
            video.close()
            audio.close()
            
            return True
            
        except Exception as e:
            raise ProcessingError(f"Failed to extract audio: {e}")
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text or None if transcription fails
            
        Raises:
            ProcessingError: If transcription fails
        """
        if self.whisper_model is None:
            raise ProcessingError("Whisper model not available for transcription")
        
        if not os.path.exists(audio_path):
            raise ProcessingError(f"Audio file not found: {audio_path}")
        
        try:
            result = self.whisper_model.transcribe(audio_path)
            return result.get("text", "").strip()
            
        except Exception as e:
            raise ProcessingError(f"Failed to transcribe audio: {e}")
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get audio file duration in seconds
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Duration in seconds
            
        Raises:
            ProcessingError: If unable to get duration
        """
        if not self.moviepy_available:
            raise ProcessingError("MoviePy not available for audio processing")
        
        if not os.path.exists(audio_path):
            raise ProcessingError(f"Audio file not found: {audio_path}")
        
        try:
            audio = self.moviepy.AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            return duration
            
        except Exception as e:
            raise ProcessingError(f"Failed to get audio duration: {e}")
