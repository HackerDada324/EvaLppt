import { Link } from "react-router-dom"
import "../../styles/Footer.css"
import { Github, Mail, MessageCircle, ArrowUpRight } from "lucide-react"

const Footer = () => {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="app-footer">
      <div className="footer-container">
        <div className="footer-section brand-section">
          <h3>Presentation Evaluator</h3>
          <p>Improve your presentation skills with AI-powered feedback and analysis.</p>
          <div className="social-links">
            <a
              href="https://github.com/yourusername/presentation-evaluator"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
            >
              <Github size={20} />
            </a>
            <a href="mailto:contact@presentationevaluator.com" aria-label="Email">
              <Mail size={20} />
            </a>
            <a href="https://twitter.com/presevaluator" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
              <MessageCircle size={20} />
            </a>
          </div>
        </div>

        <div className="footer-links-container">
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li>
                <Link to="/">Home</Link>
              </li>
              <li>
                <Link to="/upload">Upload Video</Link>
              </li>
              <li>
                <Link to="/history">Analysis History</Link>
              </li>
              <li>
                <Link to="/dashboard">Dashboard</Link>
              </li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Features</h4>
            <ul>
              <li>
                <Link to="/features/motion">Body Motion Analysis</Link>
              </li>
              <li>
                <Link to="/features/expression">Expression Analysis</Link>
              </li>
              <li>
                <Link to="/features/content">Content Analysis</Link>
              </li>
              <li>
                <Link to="/features/disfluency">Disfluency Detection</Link>
              </li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Resources</h4>
            <ul>
              <li>
                <Link to="/help" className="resource-link">
                  Help Center
                  <ArrowUpRight size={14} />
                </Link>
              </li>
              <li>
                <Link to="/faq" className="resource-link">
                  FAQ
                  <ArrowUpRight size={14} />
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/yourusername/presentation-evaluator"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="resource-link"
                >
                  GitHub Repository
                  <ArrowUpRight size={14} />
                </a>
              </li>
              <li>
                <Link to="/blog" className="resource-link">
                  Blog
                  <ArrowUpRight size={14} />
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; {currentYear} Presentation Evaluator. All Rights Reserved.</p>
        <div className="footer-legal">
          <Link to="/privacy">Privacy Policy</Link>
          <Link to="/terms">Terms of Service</Link>
          <Link to="/contact">Contact Us</Link>
        </div>
      </div>

      <div className="footer-decoration">
        <div className="footer-wave"></div>
      </div>
    </footer>
  )
}

export default Footer