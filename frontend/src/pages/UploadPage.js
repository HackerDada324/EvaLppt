import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  ArrowRight, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  Clock, 
  FileVideo, 
  Zap, 
  PictureInPicture
} from 'lucide-react';
import VideoUploader from '../components/video/VideoUploader';
import '../styles/UploadPage.css';

// Requirements data - separated for cleaner component structure
const uploadRequirements = [
  {
    id: 1,
    icon: <FileVideo size={24} />,
    title: "Video Format",
    description: "We support MP4, MOV, and AVI formats for best analysis results."
  },
  {
    id: 2,
    icon: <Clock size={24} />,
    title: "Duration",
    description: "Videos between 2-15 minutes work best for detailed analysis."
  },
  {
    id: 3,
    icon: <Zap size={24} />,
    title: "Quality",
    description: "Ensure good lighting and clear audio for the most accurate feedback."
  },
  {
    id: 4,
    icon: <PictureInPicture size={24} />,
    title: "Positioning",
    description: "Frame your video to show your full upper body for gesture analysis."
  },
  {
    id: 5,
    icon: <AlertTriangle size={24} />,
    title: "Avoid Background Noise",
    description: "Record in a quiet environment to ensure accurate speech analysis.",
    isWarning: true
  }
];

const UploadPage = () => {
  const navigate = useNavigate();
  const [showRequirements, setShowRequirements] = useState(true);
  
  // Toggle requirements section on mobile
  const toggleRequirements = () => {
    setShowRequirements(!showRequirements);
  };

  return (
    <div className="upload-page">
      {/* Background decorations */}
      <div className="upload-page-shape-1"></div>
      <div className="upload-page-shape-2"></div>
      
      <div className="section-header">
        <h1>Get comprehensive AI-powered feedback on your presentation skills</h1>
      </div>
      
      <div className="upload-page-content">
        <div className="upload-main">
          {/* VideoUploader component handles file selection, preview, upload, and processing */}
          <VideoUploader />
          
          {/* Mobile toggle for requirements */}
          <button className="toggle-requirements" onClick={toggleRequirements}>
            <span>{showRequirements ? 'Hide Requirements' : 'Show Requirements'}</span>
            <ArrowRight size={16} className={showRequirements ? 'rotate-down' : ''} />
          </button>
        </div>
        
        <div className={`upload-requirements ${showRequirements ? 'show' : 'hide'}`}>
          <div className="requirements-header">
            <h2>Upload Requirements</h2>
            <p>Follow these guidelines for the best analysis results</p>
          </div>
          
          <div className="requirements-list">
            {uploadRequirements.map(req => (
              <div key={req.id} className={`requirement-item ${req.isWarning ? 'warning' : ''}`}>
                <div className="requirement-icon">
                  {req.icon}
                </div>
                <div className="requirement-content">
                  <h4>{req.title}</h4>
                  <p>{req.description}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="requirements-note">
            <Info size={20} />
            <p>Our AI analyzes your body language, voice modulation, speech patterns, and overall presentation style to provide personalized feedback.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;