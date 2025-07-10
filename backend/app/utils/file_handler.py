"""
File handling utilities for the Auto PPT Evaluation System
"""
import os
import tempfile
import uuid
from typing import Tuple, Optional
from werkzeug.datastructures import FileStorage

from .exceptions import ValidationError
from .validators import VideoValidator


class FileHandler:
    """Handles file operations for video uploads and temporary file management"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize file handler
        
        Args:
            temp_dir: Custom temporary directory path
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.validator = VideoValidator()
    
    def save_uploaded_video(self, file: FileStorage) -> Tuple[str, str]:
        """
        Save uploaded video file to temporary location
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (video_path, audio_path) for temporary files
            
        Raises:
            ValidationError: If file validation fails
        """
        # Validate the uploaded file
        self.validator.validate_file(file)
        
        # Generate unique filenames
        unique_id = str(uuid.uuid4())
        video_filename = f"{unique_id}_{file.filename}"
        audio_filename = f"{unique_id}_audio.wav"
        
        # Create full paths
        video_path = os.path.join(self.temp_dir, video_filename)
        audio_path = os.path.join(self.temp_dir, audio_filename)
        
        # Save the video file
        try:
            file.save(video_path)
        except Exception as e:
            raise ValidationError(f"Failed to save uploaded file: {e}")
        
        return video_path, audio_path
    
    def cleanup_files(self, *file_paths: str) -> None:
        """
        Clean up temporary files
        
        Args:
            *file_paths: Variable number of file paths to delete
        """
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Warning: Failed to remove temporary file {file_path}: {e}")
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get file information
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = os.stat(file_path)
        return {
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'created_time': stat.st_ctime,
            'modified_time': stat.st_mtime,
            'filename': os.path.basename(file_path),
            'extension': os.path.splitext(file_path)[1].lower()
        }
