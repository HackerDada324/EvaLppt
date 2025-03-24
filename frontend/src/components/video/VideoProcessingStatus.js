import React, { useState, useEffect } from 'react';
import { CheckCircle, Loader } from 'lucide-react';
import '../../styles/videoProcessingStatus.css';

const VideoProcessingStatus = ({ 
  message = "Processing your video...", 
  subMessage = "This may take a few minutes",
  showProgress = false,
  progress = 0,
  processingSteps = [
    "Extracting frames",
    "Analyzing body motion",
    "Detecting facial expressions",
    "Analyzing hand gestures",
    "Evaluating posture",
    "Generating feedback"
  ]
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [dots, setDots] = useState('.');
  
  // Animation for the loading dots
  useEffect(() => {
    const dotInterval = setInterval(() => {
      setDots(prev => prev.length < 3 ? prev + '.' : '.');
    }, 500);
    
    return () => clearInterval(dotInterval);
  }, []);
  
  // Simulate progression through processing steps
  useEffect(() => {
    if (!showProgress) {
      const stepInterval = setInterval(() => {
        setCurrentStep(prev => (prev + 1) % processingSteps.length);
      }, 3000);
      
      return () => clearInterval(stepInterval);
    }
  }, [processingSteps.length, showProgress]);
  
  // Calculate which steps to mark as completed based on progress
  const getStepStatus = (index) => {
    if (showProgress) {
      const stepProgress = (index + 1) / processingSteps.length * 100;
      if (progress >= stepProgress) return 'completed';
      if (progress >= stepProgress - (100 / processingSteps.length)) return 'current';
      return 'pending';
    } else {
      if (index < currentStep) return 'completed';
      if (index === currentStep) return 'current';
      return 'pending';
    }
  };
  
  return (
    <div className="video-processing-status">
      <div className="processing-content">
        <div className="processing-animation">
          <div className="spinner">
            <Loader size={32} className="spinner-icon" />
          </div>
        </div>
        
        <div className="processing-message">
          <h3>{message}</h3>
          <p>{subMessage}</p>
        </div>
        
        <div className="processing-steps">
          {processingSteps.map((step, index) => (
            <div 
              key={index} 
              className={`processing-step ${getStepStatus(index)}`}
            >
              <div className="step-indicator">
                {getStepStatus(index) === 'completed' ? <CheckCircle size={16} /> : 
                 getStepStatus(index) === 'current' ? <span className="pulsing-dot"></span> : ''}
              </div>
              <div className="step-label">
                {step}
                {getStepStatus(index) === 'current' && <span className="loading-dots">{dots}</span>}
              </div>
            </div>
          ))}
        </div>
        
        {showProgress && (
          <div className="progress-container">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <div className="progress-percentage">{Math.round(progress)}%</div>
          </div>
        )}
      </div>
      
      <div className="processing-shape-1"></div>
      <div className="processing-shape-2"></div>
    </div>
  );
};

export default VideoProcessingStatus;