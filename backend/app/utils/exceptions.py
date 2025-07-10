"""
Custom exceptions for the Auto PPT Evaluation System
"""


class ValidationError(ValueError):
    """Raised when input validation fails"""
    pass


class ProcessingError(Exception):
    """Raised when video/audio processing fails"""
    pass


class AnalyzerError(Exception):
    """Raised when analyzer initialization or processing fails"""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass
