import React from 'react';
import { useLocation, Link } from 'react-router-dom';

const AnalysisResults = () => {
  const location = useLocation();
  const { analysisResults, videoName } = location.state || {};
  
  if (!analysisResults) {
    return (
      <div className="analysis-results-container">
        <h2>No Analysis Results</h2>
        <p>No analysis data was found. Please upload a video for analysis.</p>
        <Link to="/upload" className="button">Upload Video</Link>
      </div>
    );
  }
  
  return (
    <div className="analysis-results-container">
      <h2>Analysis Results for {videoName}</h2>
      
      <div className="results-card">
        <h3>Body Motion Analysis</h3>
        
        <div className="stats-grid">
          <div className="stat-item">
            <h4>Mean Angle</h4>
            <p className="stat-value">{analysisResults.mean_angle.toFixed(2)}°</p>
            <p className="stat-description">Average tilt angle throughout the presentation</p>
          </div>
          
          <div className="stat-item">
            <h4>Stability Score</h4>
            <p className="stat-value">{analysisResults.stability_score.toFixed(2)}</p>
            <p className="stat-description">Lower scores indicate more stable posture</p>
          </div>
          
          <div className="stat-item">
            <h4>Dominant Direction</h4>
            <p className="stat-value">{analysisResults.dominant_direction}</p>
            <p className="stat-description">Most common tilt direction</p>
          </div>
        </div>
        
        <div className="detailed-stats">
          <h4>Detailed Statistics</h4>
          <table>
            <tbody>
              <tr>
                <td>Median Angle:</td>
                <td>{analysisResults.median_angle.toFixed(2)}°</td>
              </tr>
              <tr>
                <td>Standard Deviation:</td>
                <td>{analysisResults.std_dev_angle.toFixed(2)}°</td>
              </tr>
              <tr>
                <td>Min Angle:</td>
                <td>{analysisResults.min_angle.toFixed(2)}°</td>
              </tr>
              <tr>
                <td>Max Angle:</td>
                <td>{analysisResults.max_angle.toFixed(2)}°</td>
              </tr>
              <tr>
                <td>Detection Rate:</td>
                <td>{analysisResults.detection_rate.toFixed(2)}%</td>
              </tr>
              <tr>
                <td>Duration:</td>
                <td>{analysisResults.duration_seconds.toFixed(2)} seconds</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div className="direction-breakdown">
          <h4>Direction Percentages</h4>
          <div className="direction-bars">
            {Object.entries(analysisResults.direction_percentages).map(([direction, percentage]) => (
              <div key={direction} className="direction-bar-item">
                <div className="direction-label">{direction}</div>
                <div className="direction-bar-container">
                  <div 
                    className="direction-bar-fill"
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
                <div className="direction-percentage">{percentage.toFixed(1)}%</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="results-actions">
        <Link to="/upload" className="button">Analyze Another Video</Link>
        <Link to="/" className="button button-secondary">Back to Dashboard</Link>
      </div>
    </div>
  );
};

export default AnalysisResults;