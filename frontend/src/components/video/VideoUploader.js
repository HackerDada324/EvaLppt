import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisService } from '../../services/analysisService';
import { Upload, X, AlertCircle, CheckCircle, Info } from 'lucide-react';
import VideoPlayer from './VideoPlayer';
import VideoProcessingStatus from './VideoProcessingStatus';
import '../../styles/videoUploader.css';

const VideoUploader = () => {
  // State hooks
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [isHovering, setIsHovering] = useState(false);
  
  // Refs
  const fileInputRef = useRef(null);
  
  // Navigation
  const navigate = useNavigate();
  
  // Clean up object URLs on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);
  
  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // Check if file is a video
    if (!selectedFile.type.startsWith('video/')) {
      setError('Please select a valid video file');
      return;
    }

    // Check file size (limit to 100MB for example)
    if (selectedFile.size > 100 * 1024 * 1024) {
      setError('File size exceeds 100MB limit');
      return;
    }

    // Clean up previous preview if it exists
    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setFile(selectedFile);
    setError(null);

    // Create video preview
    const previewUrl = URL.createObjectURL(selectedFile);
    setPreview(previewUrl);
  };

  // Handle drag-and-drop functionality
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isHovering) setIsHovering(true);
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (isHovering) setIsHovering(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsHovering(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (!droppedFile) return;
    
    // Check if file is a video
    if (!droppedFile.type.startsWith('video/')) {
      setError('Please drop a valid video file');
      return;
    }
    
    // Check file size (limit to 100MB for example)
    if (droppedFile.size > 100 * 1024 * 1024) {
      setError('File size exceeds 100MB limit');
      return;
    }
    
    // Clean up previous preview if it exists
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    
    setFile(droppedFile);
    setError(null);
    const previewUrl = URL.createObjectURL(droppedFile);
    setPreview(previewUrl);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a video file first');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);
      
      // Upload phase
      const uploadResponse = await analysisService.uploadVideo(file, {
        targetFps: 5, 
        onProgress: (progress) => {
          setUploadProgress(progress);
        }
      });
      
      // Processing phase (after upload completes)
      setUploading(false);
      setProcessing(true);
      
      const analysisId = uploadResponse.data.analysisId;
      
      // Poll for processing status
      const pollingInterval = setInterval(async () => {
        try {
          const statusResponse = await analysisService.getAnalysisStatus(analysisId);
          if (statusResponse.data.status === 'completed') {
            clearInterval(pollingInterval);
            
            // Get full analysis results
            const analysisResults = await analysisService.getAnalysisResults(analysisId);
            
            // Navigate to results page with the data
            navigate(`/analysis/${analysisId}`);
          } else if (statusResponse.data.status === 'failed') {
            clearInterval(pollingInterval);
            setError('Analysis failed. Please try again with a different video.');
            setProcessing(false);
          }
        } catch (err) {
          clearInterval(pollingInterval);
          console.error('Status check error:', err);
          setError('Failed to check processing status. Please try again.');
          setProcessing(false);
        }
      }, 3000); // Check every 3 seconds
      
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.error || 'Failed to upload video. Please try again.');
      setUploading(false);
      setProcessing(false);
    }
  };
  
  const triggerFileInput = () => {
    if (!uploading && !processing) {
      fileInputRef.current.click();
    }
  };
  
  const resetUpload = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setFile(null);
    setPreview(null);
    setError(null);
  };

  return (
    <div className="video-uploader-container">
      <div className="section-header">
        <h2>Upload Presentation Video</h2>
        <p>Upload your video to receive AI-powered feedback on your presentation skills</p>
      </div>
      
      {/* Main upload area */}
      <div 
        className={`upload-area ${file ? 'has-file' : ''} ${isHovering ? 'dragging' : ''} ${(uploading || processing) ? 'disabled' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={triggerFileInput}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="video/*"
          style={{ display: 'none' }}
          disabled={uploading || processing}
        />
        
        {preview ? (
          <div className="video-preview">
            <VideoPlayer 
              src={preview} 
              title={file.name}
              width="100%"
              height="auto"
              controls={true}
            />
            <div className="video-info">
              <p className="video-name">{file.name}</p>
              <p className="video-size">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
              {!uploading && !processing && (
                <button className="secondary-button" onClick={(e) => { e.stopPropagation(); resetUpload(); }}>
                  <X size={16} />
                  Choose Different Video
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="upload-prompt">
            <div className="upload-icon">
              <Upload size={40} />
            </div>
            <p>Drag and drop your video here or click to browse</p>
            <p className="upload-hint">Supported formats: MP4, MOV, AVI, etc.</p>
            <p className="upload-hint">Maximum size: 100MB</p>
          </div>
        )}
        
        <div className="upload-shape-1"></div>
        <div className="upload-shape-2"></div>
      </div>
      
      {/* Error message display */}
      {error && (
        <div className="error-message">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}
      
      {/* Upload/Processing status display */}
      {uploading && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p>Uploading... {uploadProgress}%</p>
        </div>
      )}
      
      {processing && (
        <VideoProcessingStatus 
          message="Analyzing your presentation..."
          subMessage="This may take a few minutes. Please don't close this page."
        />
      )}
      
      {/* Action button */}
      {!uploading && !processing && (
      <div className="upload-button-container">
        <button 
          className="primary-button upload-analyze-btn" 
          onClick={handleUpload}
          disabled={!file || uploading || processing}
        >
          <Upload size={20} />
          <span>Upload and Analyze</span>
        </button>
      </div>
    )}
      
      {/* Instructions */}
      <div className="upload-instructions">
        <div className="instructions-header">
          <Info size={20} />
          <h3>Guidelines for Best Results:</h3>
        </div>
        <ul>
          <li>Ensure good lighting and clear audio</li>
          <li>Position the camera to capture your full upper body</li>
          <li>Record in a quiet environment with minimal background noise</li>
          <li>Speak clearly and at a normal pace</li>
          <li>Recommended video length: 3-10 minutes</li>
        </ul>
      </div>
    </div>
  );
};

export default VideoUploader;