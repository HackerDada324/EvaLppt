import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisService } from '../../services/analysisService';

const VideoUploader = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

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

    setFile(selectedFile);
    setError(null);

    // Create video preview
    const previewUrl = URL.createObjectURL(selectedFile);
    setPreview(previewUrl);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      setFile(droppedFile);
      setError(null);
      const previewUrl = URL.createObjectURL(droppedFile);
      setPreview(previewUrl);
    } else {
      setError('Please drop a valid video file');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a video file first');
      return;
    }

    try {
      setUploading(true);
      setUploadProgress(0);
      
      // Custom axios request to track progress
      const formData = new FormData();
      formData.append('video', file);
      
      const response = await analysisService.uploadVideo(file);
      
      // Navigate to analysis page with the returned ID
      navigate(`/analysis/${response.data.analysisId}`);
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload video. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="video-uploader-container">
      <h2>Upload Presentation Video</h2>
      
      <div 
        className={`upload-area ${file ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={triggerFileInput}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="video/*"
          style={{ display: 'none' }}
        />
        
        {preview ? (
          <div className="video-preview">
            <video src={preview} controls width="100%" height="auto" />
            <p>{file.name} ({(file.size / (1024 * 1024)).toFixed(2)} MB)</p>
          </div>
        ) : (
          <div className="upload-prompt">
            <div className="upload-icon">📤</div>
            <p>Drag and drop your video here or click to browse</p>
            <p className="upload-hint">Supported formats: MP4, MOV, AVI, etc.</p>
          </div>
        )}
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      {uploading ? (
        <div className="upload-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p>Uploading... {uploadProgress}%</p>
        </div>
      ) : (
        <button 
          className="upload-button" 
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          Upload and Analyze
        </button>
      )}
      
      <div className="upload-instructions">
        <h3>Guidelines for Best Results:</h3>
        <ul>
          <li>Ensure good lighting and clear audio</li>
          <li>Position the camera to capture your full upper body</li>
          <li>Record in a quiet environment with minimal background noise</li>
          <li>Speak clearly and at a normal pace</li>
        </ul>
      </div>
    </div>
  );
};

export default VideoUploader;