import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisService } from '../services/analysisService';
import { Upload, ArrowRight, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import VideoUploader from '../components/video/VideoUploader';
import '../styles/UploadPage.css';

const UploadPage = () => {
  const navigate = useNavigate();
  const [showRequirements, setShowRequirements] = useState(true);
  
  // Toggle requirements section on mobile
  const toggleRequirements = () => {
    setShowRequirements(!showRequirements);
  };

  return (
    <div className="upload-page">
      <div className="section-header">
        <h1>Upload Your Presentation</h1>
        <p>Get comprehensive AI-powered feedback on your presentation skills</p>
      </div>
      
      <div className="upload-page-content">
        <div className="upload-main">
          {/* VideoUploader component handles file selection, preview, upload, and processing */}
          <VideoUploader />
          
          {/* Mobile toggle for requirements */}
          <button className="toggle-requirements" onClick={toggleRequirements}>
            {showRequirements ? 'Hide Requirements' : 'Show Requirements'}
            <ArrowRight size={16} className={showRequirements ? 'rotate-down' : ''} />
          </button>
        </div>
        
        <div className={`upload-requirements ${showRequirements ? 'show' : 'hide'}`}>
          <div className="requirements-header">
            <h2>Upload Requirements</h2>
            <p>Follow these guidelines for the best analysis results</p>
          </div>
          
          <div className="requirements-list">
            <div className="requirement-item">
              <div className="requirement-icon">
                <CheckCircle size={24} />
              </div>
              <div className="requirement-content">
                <h4>Video Format</h4>
                <p>We support MP4, MOV, and AVI formats for best analysis results.</p>
              </div>
            </div>
            
            <div className="requirement-item">
              <div className="requirement-icon">
                <CheckCircle size={24} />
              </div>
              <div className="requirement-content">
                <h4>Duration</h4>
                <p>Videos between 2-15 minutes work best for detailed analysis.</p>
              </div>
            </div>
            
            <div className="requirement-item">
              <div className="requirement-icon">
                <CheckCircle size={24} />
              </div>
              <div className="requirement-content">
                <h4>Quality</h4>
                <p>Ensure good lighting and clear audio for the most accurate feedback.</p>
              </div>
            </div>
            
            <div className="requirement-item">
              <div className="requirement-icon">
                <CheckCircle size={24} />
              </div>
              <div className="requirement-content">
                <h4>Positioning</h4>
                <p>Frame your video to show your full upper body for gesture analysis.</p>
              </div>
            </div>
            
            <div className="requirement-item">
              <div className="requirement-icon">
                <AlertTriangle size={24} />
              </div>
              <div className="requirement-content">
                <h4>Avoid Background Noise</h4>
                <p>Record in a quiet environment to ensure accurate speech analysis.</p>
              </div>
            </div>
          </div>
          
          <div className="requirements-note">
            <Info size={20} />
            <p>Our AI analyzes your body language, voice modulation, speech patterns, and overall presentation style to provide personalized feedback.</p>
          </div>
        </div>
      </div>
      
      <div className="upload-page-shape-1"></div>
      <div className="upload-page-shape-2"></div>
    </div>
  );
};

export default UploadPage;