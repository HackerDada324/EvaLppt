import { Link } from "react-router-dom"
import { Github } from "lucide-react"
import "../../styles/Footer.css"

const Footer = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="app-footer">
      <div className="footer-container simplified">
        <div className="footer-content">
          <div className="footer-branding">
            <h3>Presentation Evaluator</h3>
            <p>Improve your presentation skills with AI-powered feedback and analysis.</p>
          </div>
          
          <div className="footer-social">
            <a
              href="https://github.com/yourusername/presentation-evaluator"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
              className="github-link"
            >
              <Github size={20} />
              <span>View on GitHub</span>
            </a>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; {currentYear} Presentation Evaluator. All Rights Reserved.</p>
        </div>
      </div>
      
      <div className="footer-decoration">
        <div className="footer-wave"></div>
      </div>
    </footer>
  )
}

export default Footer