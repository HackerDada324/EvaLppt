"""
Validators for the Auto PPT Evaluation System
"""
import os
from typing import List
from werkzeug.datastructures import FileStorage

from .exceptions import ValidationError


class VideoValidator:
    """Validates video files for processing"""
    
    # Default supported formats
    SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    
    # Default maximum file size (100MB)
    MAX_FILE_SIZE_MB = 100
    
    def __init__(self, 
                 supported_formats: List[str] = None,
                 max_file_size_mb: float = None):
        """
        Initialize validator
        
        Args:
            supported_formats: List of supported file extensions
            max_file_size_mb: Maximum file size in MB
        """
        self.supported_formats = supported_formats or self.SUPPORTED_FORMATS
        self.max_file_size_mb = max_file_size_mb or self.MAX_FILE_SIZE_MB
    
    def validate_file(self, file: FileStorage) -> None:
        """
        Validate uploaded video file
        
        Args:
            file: Uploaded file object
            
        Raises:
            ValidationError: If validation fails
        """
        if not file:
            raise ValidationError("No file provided")
        
        if not file.filename:
            raise ValidationError("No filename provided")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValidationError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
        
        # Check file size (if we can get it)
        if hasattr(file, 'content_length') and file.content_length:
            file_size_mb = file.content_length / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                raise ValidationError(
                    f"File too large: {file_size_mb:.1f}MB. "
                    f"Maximum allowed: {self.max_file_size_mb}MB"
                )
    
    def validate_file_path(self, file_path: str) -> None:
        """
        Validate a file path
        
        Args:
            file_path: Path to the file
            
        Raises:
            ValidationError: If validation fails
        """
        if not os.path.exists(file_path):
            raise ValidationError(f"File does not exist: {file_path}")
        
        if not os.path.isfile(file_path):
            raise ValidationError(f"Path is not a file: {file_path}")
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValidationError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise ValidationError(
                f"File too large: {file_size_mb:.1f}MB. "
                f"Maximum allowed: {self.max_file_size_mb}MB"
            )
