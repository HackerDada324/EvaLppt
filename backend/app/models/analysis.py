"""
Analysis Record Model for tracking presentation analysis data
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import uuid


class AnalysisStatus(Enum):
    """Enumeration for analysis status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AnalysisRecord:
    """
    Data model for tracking presentation analysis records
    """
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    status: AnalysisStatus = AnalysisStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    progress: int = 0
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'analysis_id': self.analysis_id,
            'filename': self.filename,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'progress': self.progress,
            'results': self.results,
            'error_message': self.error_message,
            'metadata': self.metadata
        }
    
    def update_status(self, status: AnalysisStatus, error_message: Optional[str] = None):
        """Update analysis status"""
        self.status = status
        self.updated_at = datetime.now()
        if error_message:
            self.error_message = error_message
    
    def update_progress(self, progress: int):
        """Update analysis progress"""
        self.progress = max(0, min(100, progress))
        self.updated_at = datetime.now()
    
    def set_results(self, results: Dict[str, Any]):
        """Set analysis results"""
        self.results = results
        self.status = AnalysisStatus.COMPLETED
        self.progress = 100
        self.updated_at = datetime.now()
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
        self.updated_at = datetime.now()
