import React from 'react';
import '../../styles/Loading.css'; // You'll need to create this CSS file

const Loading = ({ message = 'Loading...', fullScreen = false }) => {
  const loadingClasses = fullScreen ? 'loading-container full-screen' : 'loading-container';
  
  return (
    <div className={loadingClasses}>
      <div className="loading-spinner">
        <div className="spinner-circle"></div>
        <div className="spinner-circle inner"></div>
      </div>
      
      {message && <p className="loading-message">{message}</p>}
    </div>
  );
};

// Additional loading variations you might need
export const ProcessingLoader = () => {
  return (
    <Loading 
      message="Processing your video. This may take a few minutes..." 
      fullScreen={true} 
    />
  );
};

export const AnalysisLoader = () => {
  return (
    <Loading 
      message="Analyzing presentation data..." 
      fullScreen={false} 
    />
  );
};

export const ButtonLoader = ({ small = false }) => {
  return (
    <div className={`button-loader ${small ? 'small' : ''}`}>
      <div className="spinner-dot"></div>
      <div className="spinner-dot"></div>
      <div className="spinner-dot"></div>
    </div>
  );
};

export default Loading;