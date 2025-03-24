import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { analysisService } from '../services/analysisService';
import '../styles/AnalysisPage.css';

// Import analysis result components
import AudioAnalysisResults from '../components/analysis/AudioAnalysisResults';
import ContentAnalysisResults from '../components/analysis/ContentAnalysisResults';
import DisfluencyAnalysisResults from '../components/analysis/DisfluencyAnalysisResults';
import MotionAnalysisResults from '../components/analysis/MotionAnalysisResults';
import ExpressionAnalysisResults from '../components/analysis/ExpressionAnalysisResults';
import SummaryDashboard from '../components/analysis/SummaryDashboard';

const AnalysisPage = () => {
  const { id } = useParams(); // Get the analysis ID from URL
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');

  useEffect(() => {
    const fetchAnalysisData = async () => {
      try {
        setLoading(true);
        // Poll for results every 3 seconds until complete
        const intervalId = setInterval(async () => {
          const response = await analysisService.getAnalysisResults(id);
          
          if (response.data.status === 'completed' || response.data.status === 'failed') {
            clearInterval(intervalId);
            setAnalysisData(response.data);
            setLoading(false);
          } else {
            // Update progress information
            setAnalysisData(response.data);
          }
        }, 3000);
        
        // Clear interval on component unmount
        return () => clearInterval(intervalId);
      } catch (err) {
        console.error('Error fetching analysis:', err);
        setError('Failed to load analysis results. Please try again.');
        setLoading(false);
      }
    };

    fetchAnalysisData();
  }, [id]);

  const renderContent = () => {
    if (loading && (!analysisData || analysisData.status !== 'completed')) {
      return (
        <div className="analysis-loading">
          <h2>Processing Your Video</h2>
          <div className="analysis-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${analysisData?.progress || 0}%` }}
              ></div>
            </div>
            <p>{analysisData?.statusMessage || 'Analyzing your presentation...'}</p>
            <p className="progress-percentage">{analysisData?.progress || 0}% Complete</p>
          </div>
        </div>
      );
    }

    if (error || (analysisData && analysisData.status === 'failed')) {
      return (
        <div className="analysis-error">
          <h2>Analysis Failed</h2>
          <p>{error || analysisData?.error || 'An unknown error occurred during analysis.'}</p>
          <button onClick={() => window.history.back()} className="back-button">
            Go Back
          </button>
        </div>
      );
    }

    return (
      <>
        <div className="video-container">
          <video 
            src={analysisData.videoUrl} 
            controls 
            width="100%" 
            height="auto"
          />
        </div>

        <div className="analysis-tabs">
          <button 
            className={`tab-button ${activeTab === 'summary' ? 'active' : ''}`}
            onClick={() => setActiveTab('summary')}
          >
            Summary
          </button>
          <button 
            className={`tab-button ${activeTab === 'content' ? 'active' : ''}`}
            onClick={() => setActiveTab('content')}
          >
            Content
          </button>
          <button 
            className={`tab-button ${activeTab === 'audio' ? 'active' : ''}`}
            onClick={() => setActiveTab('audio')}
          >
            Speech
          </button>
          <button 
            className={`tab-button ${activeTab === 'disfluency' ? 'active' : ''}`}
            onClick={() => setActiveTab('disfluency')}
          >
            Disfluency
          </button>
          <button 
            className={`tab-button ${activeTab === 'motion' ? 'active' : ''}`}
            onClick={() => setActiveTab('motion')}
          >
            Motion
          </button>
          <button 
            className={`tab-button ${activeTab === 'expression' ? 'active' : ''}`}
            onClick={() => setActiveTab('expression')}
          >
            Expression
          </button>
        </div>

        <div className="analysis-content">
          {activeTab === 'summary' && (
            <SummaryDashboard data={analysisData} />
          )}
          {activeTab === 'content' && (
            <ContentAnalysisResults data={analysisData.contentAnalysis} />
          )}
          {activeTab === 'audio' && (
            <AudioAnalysisResults data={analysisData.audioAnalysis} />
          )}
          {activeTab === 'disfluency' && (
            <DisfluencyAnalysisResults data={analysisData.disfluencyAnalysis} />
          )}
          {activeTab === 'motion' && (
            <MotionAnalysisResults data={analysisData.motionAnalysis} />
          )}
          {activeTab === 'expression' && (
            <ExpressionAnalysisResults data={analysisData.expressionAnalysis} />
          )}
        </div>
      </>
    );
  };

  return (
    <div className="analysis-page">
      <h1>Presentation Analysis</h1>
      <div className="analysis-container">
        {renderContent()}
      </div>
    </div>
  );
};

export default AnalysisPage;