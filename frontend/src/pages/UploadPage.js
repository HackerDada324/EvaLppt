import React from 'react';
import VideoUploader from '../components/video/VideoUploader';
import '../styles/UploadPage.css';

const UploadPage = () => {
  return (
    <div className="upload-page">
      <h1>Upload Your Presentation</h1>
      <p>Upload a video of your presentation for AI analysis</p>
      <VideoUploader />
    </div>
  );
};

export default UploadPage;