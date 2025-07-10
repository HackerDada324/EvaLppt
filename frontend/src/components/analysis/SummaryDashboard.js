import React from 'react';
import { BarChart2, Mic, Video, Smile, CheckCircle, AlertTriangle, ThumbsUp } from 'lucide-react';

const SummaryDashboard = ({ data }) => {
    if (!data) return <div>No data available</div>;

    // Calculate overall score based on various metrics
    const calculateOverallScore = () => {
        if (!data) return 0;
        
        const scores = [
            data.body_motion?.stability_score || 0,
            data.head_motion?.stability_score || 0,
            data.hand_motion?.engagement_score || 0,
            data.audio?.clarity_score || 0,
            data.content?.structure_score || 0,
            data.expression?.engagement_score || 0
        ];
        
        // Filter out zeros and calculate average
        const validScores = scores.filter(score => score > 0);
        return validScores.length > 0 
            ? Math.round(validScores.reduce((a, b) => a + b, 0) / validScores.length * 10) / 10
            : 0;
    };
    
    const overallScore = calculateOverallScore();
    
    // Function to determine score color
    const getScoreColor = (score) => {
        if (score >= 8) return '#4CAF50'; // Green for excellent
        if (score >= 6) return '#2196F3'; // Blue for good
        if (score >= 4) return '#FF9800'; // Orange for average
        return '#F44336'; // Red for poor
    };

    return (
        <div className="summary-dashboard">
            <div className="overall-score-card">
                <div className="score-circle" style={{ borderColor: getScoreColor(overallScore) }}>
                    <span className="score-value" style={{ color: getScoreColor(overallScore) }}>
                        {overallScore}/10
                    </span>
                </div>
                <h2>Overall Presentation Score</h2>
                <p className="score-description">
                    Based on your performance across body language, speech, and content
                </p>
            </div>
            
            <div className="score-cards-grid">
                {/* Motion Analysis */}
                <div className="score-card">
                    <div className="card-header">
                        <Video size={20} />
                        <h3>Body Motion</h3>
                    </div>
                    <div className="card-body">
                        <div className="metric">
                            <span className="metric-label">Stability</span>
                            <div className="metric-bar">
                                <div 
                                    className="metric-fill" 
                                    style={{ 
                                        width: `${(data.body_motion?.stability_score || 0) * 10}%`,
                                        backgroundColor: getScoreColor(data.body_motion?.stability_score || 0)
                                    }}
                                ></div>
                            </div>
                            <span className="metric-value">{data.body_motion?.stability_score || 0}/10</span>
                        </div>
                        <div className="key-insight">
                            <ThumbsUp size={16} />
                            <span>
                                Dominant direction: {data.body_motion?.dominant_direction || 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>
                
                {/* Speech Analysis */}
                <div className="score-card">
                    <div className="card-header">
                        <Mic size={20} />
                        <h3>Speech Quality</h3>
                    </div>
                    <div className="card-body">
                        <div className="metric">
                            <span className="metric-label">Clarity</span>
                            <div className="metric-bar">
                                <div 
                                    className="metric-fill" 
                                    style={{ 
                                        width: `${(data.audio?.clarity_score || 0) * 10}%`,
                                        backgroundColor: getScoreColor(data.audio?.clarity_score || 0)
                                    }}
                                ></div>
                            </div>
                            <span className="metric-value">{data.audio?.clarity_score || 0}/10</span>
                        </div>
                        <div className="key-insight">
                            <ThumbsUp size={16} />
                            <span>
                                {data.audio?.speech_rate || 0} words per minute
                            </span>
                        </div>
                    </div>
                </div>
                
                {/* Content Analysis */}
                <div className="score-card">
                    <div className="card-header">
                        <CheckCircle size={20} />
                        <h3>Content Structure</h3>
                    </div>
                    <div className="card-body">
                        <div className="metric">
                            <span className="metric-label">Structure</span>
                            <div className="metric-bar">
                                <div 
                                    className="metric-fill" 
                                    style={{ 
                                        width: `${(data.content?.structure_score || 0) * 10}%`,
                                        backgroundColor: getScoreColor(data.content?.structure_score || 0)
                                    }}
                                ></div>
                            </div>
                            <span className="metric-value">{data.content?.structure_score || 0}/10</span>
                        </div>
                        <div className="key-insight">
                            <ThumbsUp size={16} />
                            <span>
                                {data.content?.key_points || 0} key points identified
                            </span>
                        </div>
                    </div>
                </div>
                
                {/* Disfluency Analysis */}
                <div className="score-card">
                    <div className="card-header">
                        <AlertTriangle size={20} />
                        <h3>Speech Disfluencies</h3>
                    </div>
                    <div className="card-body">
                        <div className="metric">
                            <span className="metric-label">Filler Words</span>
                            <div className="metric-bar">
                                <div 
                                    className="metric-fill" 
                                    style={{ 
                                        width: `${Math.min(data.disfluency?.filler_words_per_minute || 0, 10) * 10}%`,
                                        backgroundColor: getScoreColor(10 - Math.min(data.disfluency?.filler_words_per_minute || 0, 10))
                                    }}
                                ></div>
                            </div>
                            <span className="metric-value">{data.disfluency?.filler_words_per_minute || 0}/min</span>
                        </div>
                        <div className="key-insight">
                            <AlertTriangle size={16} />
                            <span>
                                {data.disfluency?.filler_words_count || 0} total filler words detected
                            </span>
                        </div>
                    </div>
                </div>
                
                {/* Expression Analysis */}
                <div className="score-card">
                    <div className="card-header">
                        <Smile size={20} />
                        <h3>Facial Expressions</h3>
                    </div>
                    <div className="card-body">
                        <div className="metric">
                            <span className="metric-label">Engagement</span>
                            <div className="metric-bar">
                                <div 
                                    className="metric-fill" 
                                    style={{ 
                                        width: `${(data.expression?.engagement_score || 0) * 10}%`,
                                        backgroundColor: getScoreColor(data.expression?.engagement_score || 0)
                                    }}
                                ></div>
                            </div>
                            <span className="metric-value">{data.expression?.engagement_score || 0}/10</span>
                        </div>
                        <div className="key-insight">
                            <ThumbsUp size={16} />
                            <span>
                                Dominant emotion: {data.expression?.dominant_emotion || 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div className="summary-insights">
                <h3>Key Insights</h3>
                <ul>
                    <li>Your presentation had an overall score of {overallScore}/10</li>
                    <li>Your dominant body position was facing {data.body_motion?.dominant_direction || 'center'}</li>
                    <li>Your speech pace was {data.audio?.speech_rate || 0} words per minute (optimal is 120-160)</li>
                    <li>You used {data.disfluency?.filler_words_count || 0} filler words throughout your presentation</li>
                    <li>Your strongest area: {data.content?.structure_score > data.expression?.engagement_score ? 'Content Structure' : 'Facial Expressions'}</li>
                </ul>
            </div>
        </div>
    );
};

export default SummaryDashboard;