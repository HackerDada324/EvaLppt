import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/HomePage.css';

const HomePage = () => {
  return (
    <div className="home-page">
      <header>
        <h1>AI Presentation Evaluator</h1>
        <p>Get instant feedback on your presentation skills</p>
      </header>
      
      <section className="features">
        <div className="feature-card">
          <h3>Content Analysis</h3>
          <p>Analyze the quality and structure of your presentation content</p>
        </div>
        <div className="feature-card">
          <h3>Speech Analysis</h3>
          <p>Evaluate your speech clarity, pace, and delivery</p>
        </div>
        <div className="feature-card">
          <h3>Body Language</h3>
          <p>Review your body motion, gestures, and posture</p>
        </div>
        <div className="feature-card">
          <h3>Facial Expressions</h3>
          <p>Analyze your facial expressions and engagement</p>
        </div>
      </section>
      
      <div className="cta-container">
        <Link to="/upload" className="cta-button">
          Upload Your Presentation
        </Link>
      </div>
    </div>
  );
};

export default HomePage;