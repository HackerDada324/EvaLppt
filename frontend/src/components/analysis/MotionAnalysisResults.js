import React from 'react';
import { ArrowLeft, Video, ThumbsUp, Info, AlertTriangle } from 'lucide-react';
import { useLocation, Link } from 'react-router-dom';

const MotionAnalysisResults = () => {
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
  
  // Function to determine score color
  const getScoreColor = (score) => {
    if (score >= 8) return '#4CAF50'; // Green for excellent
    if (score >= 6) return '#2196F3'; // Blue for good
    if (score >= 4) return '#FF9800'; // Orange for average
    return '#F44336'; // Red for poor
  };

  // Get body motion data
  const bodyMotion = analysisResults.body_motion || {};
  const headMotion = analysisResults.head_motion || {};
  const handMotion = analysisResults.hand_motion || {};
  
  return (
    <div className="analysis-results-container">
      <h2>Analysis Results for {videoName}</h2>
      
      <div className="results-card">
        <div className="section-header">
          <Video size={24} />
          <h3>Body Motion Analysis</h3>
        </div>
        
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-header">
              <h4>Stability Score</h4>
              <div className="score-circle" style={{ borderColor: getScoreColor(bodyMotion.stability_score || 0) }}>
                <span>{bodyMotion.stability_score?.toFixed(1) || 'N/A'}</span>
              </div>
            </div>
            <p className="metric-description">How stable your body position was during the presentation</p>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              <h4>Dominant Direction</h4>
              <div className="direction-indicator">
                <span>{bodyMotion.dominant_direction || 'Center'}</span>
              </div>
            </div>
            <p className="metric-description">Your most common body orientation</p>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              <h4>Mean Angle</h4>
              <div className="angle-indicator">
                <span>{bodyMotion.mean_angle?.toFixed(1) || 'N/A'}°</span>
              </div>
            </div>
            <p className="metric-description">Average body tilt angle throughout your presentation</p>
          </div>
        </div>
        
        {bodyMotion.direction_percentages && (
          <div className="direction-distribution">
            <h4>Direction Distribution</h4>
            <div className="direction-bars">
              {Object.entries(bodyMotion.direction_percentages).map(([direction, percentage]) => (
                <div key={direction} className="direction-bar-item">
                  <span className="direction-label">{direction}</span>
                  <div className="direction-bar-container">
                    <div 
                      className="direction-bar-fill" 
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: direction === bodyMotion.dominant_direction ? '#2196F3' : '#94CEF2'
                      }}
                    ></div>
                  </div>
                  <span className="direction-percentage">{percentage}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="detailed-stats">
          <h4>Detailed Body Motion Statistics</h4>
          <div className="stats-table">
            <div className="stats-row">
              <div className="stats-cell">
                <span className="stats-label">Median Angle:</span>
                <span className="stats-value">{bodyMotion.median_angle?.toFixed(2) || 'N/A'}°</span>
              </div>
              <div className="stats-cell">
                <span className="stats-label">Standard Deviation:</span>
                <span className="stats-value">{bodyMotion.std_dev_angle?.toFixed(2) || 'N/A'}°</span>
              </div>
            </div>
            <div className="stats-row">
              <div className="stats-cell">
                <span className="stats-label">Min Angle:</span>
                <span className="stats-value">{bodyMotion.min_angle?.toFixed(2) || 'N/A'}°</span>
              </div>
              <div className="stats-cell">
                <span className="stats-label">Max Angle:</span>
                <span className="stats-value">{bodyMotion.max_angle?.toFixed(2) || 'N/A'}°</span>
              </div>
            </div>
            <div className="stats-row">
              <div className="stats-cell">
                <span className="stats-label">Frames Analyzed:</span>
                <span className="stats-value">{bodyMotion.frames_analyzed || 'N/A'}</span>
              </div>
              <div className="stats-cell">
                <span className="stats-label">Detection Rate:</span>
                <span className="stats-value">{(bodyMotion.detection_rate * 100)?.toFixed(1) || 'N/A'}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="results-card">
        <div className="section-header">
          <Video size={24} />
          <h3>Head Motion Analysis</h3>
        </div>
        
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-header">
              <h4>Stability Score</h4>
              <div className="score-circle" style={{ borderColor: getScoreColor(headMotion.stability_score || 0) }}>
                <span>{headMotion.stability_score?.toFixed(1) || 'N/A'}</span>
              </div>
            </div>
            <p className="metric-description">How stable your head position was during the presentation</p>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              <h4>Dominant Direction</h4>
              <div className="direction-indicator">
                <span>{headMotion.dominant_direction || 'Center'}</span>
              </div>
            </div>
            <p className="metric-description">Your most common head orientation</p>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              <h4>Motion Rate</h4>
              <div className="rate-indicator">
                <span>{headMotion.motion_rate || 'Moderate'}</span>
              </div>
            </div>
            <p className="metric-description">Rate of head movement throughout your presentation</p>
          </div>
        </div>
      </div>
      
      <div className="results-card">
        <div className="section-header">
          <Video size={24} />
          <h3>Hand Motion Analysis</h3>
        </div>
        
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-header">
              <h4>Activity Level</h4>
              <div className="activity-indicator">
                <span>{handMotion.activity_level || 'Moderate'}</span>
              </div>
            </div>
            <p className="metric-description">How actively you used hand gestures during your presentation</p>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              <h4>Gesture Count</h4>
              <div className="count-indicator">
                <span>{handMotion.gesture_count || 'N/A'}</span>
              </div>
            </div>
            <p className="metric-description">Number of distinct hand gestures detected</p>
          </div>
          
          <div className="metric-card">
            <div className="metric-header">
              <h4>Engagement Score</h4>
              <div className="score-circle" style={{ borderColor: getScoreColor(handMotion.engagement_score || 0) }}>
                <span>{handMotion.engagement_score?.toFixed(1) || 'N/A'}</span>
              </div>
            </div>
            <p className="metric-description">How effectively your hand gestures enhanced engagement</p>
          </div>
        </div>
      </div>
      
      <div className="insights-section">
        <div className="section-header">
          <ThumbsUp size={24} />
          <h3>Motion Insights & Recommendations</h3>
        </div>
        
        <div className="insight-cards">
          <div className="insight-card">
            <div className="insight-header">
              <Info size={20} />
              <h4>Body Stability</h4>
            </div>
            <p>
              {bodyMotion.stability_score >= 7 ? 
                'You maintained excellent body stability throughout your presentation, which conveys confidence.' : 
                'Try to maintain a more stable body position to convey greater confidence.'}
            </p>
          </div>
          
          <div className="insight-card">
            <div className="insight-header">
              <Info size={20} />
              <h4>Head Movement</h4>
            </div>
            <p>
              {headMotion.stability_score >= 7 ? 
                'Your head movements were natural and helped emphasize key points.' : 
                'Work on more deliberate head movements to emphasize key points and maintain audience engagement.'}
            </p>
          </div>
          
          <div className="insight-card">
            <div className="insight-header">
              <Info size={20} />
              <h4>Hand Gestures</h4>
            </div>
            <p>
              {handMotion.activity_level === 'high' ? 
                'Your animated hand gestures helped illustrate your points effectively.' : 
                'Consider incorporating more deliberate hand gestures to emphasize key points and increase audience engagement.'}
            </p>
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

export default MotionAnalysisResults;