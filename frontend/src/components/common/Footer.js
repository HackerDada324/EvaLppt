import React from 'react';
import { Link } from 'react-router-dom';
import '../../styles/Footer.css'; // You'll need to create this CSS file

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="app-footer">
      <div className="footer-container">
        <div className="footer-section">
          <h3>Presentation Evaluator</h3>
          <p>Improve your presentation skills with AI-powered feedback and analysis.</p>
        </div>
        
        <div className="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/upload">Upload Video</Link></li>
            <li><Link to="/history">Analysis History</Link></li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4>Features</h4>
          <ul>
            <li>Body Motion Analysis</li>
            <li>Expression Analysis</li>
            <li>Content Analysis</li>
            <li>Disfluency Detection</li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4>Resources</h4>
          <ul>
            <li><Link to="/help">Help Center</Link></li>
            <li><Link to="/faq">FAQ</Link></li>
            <li><a href="https://github.com/yourusername/presentation-evaluator" target="_blank" rel="noopener noreferrer">
              GitHub Repository
            </a></li>
          </ul>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>&copy; {currentYear} Presentation Evaluator. All Rights Reserved.</p>
        <div className="footer-legal">
          <Link to="/privacy">Privacy Policy</Link>
          <Link to="/terms">Terms of Service</Link>
        </div>
      </div>
    </footer>
  );
};

export default Footer;