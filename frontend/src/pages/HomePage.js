import { Link } from "react-router-dom"
import "../styles/HomePage.css"
import { ArrowRight, CheckCircle, Mic, Video, BarChart2, Smile, Award, Clock } from "lucide-react"

const HomePage = () => {
  return (
    <div className="home-page">
      {/* Background decorations */}
      <div className="bg-decoration bg-decoration-1"></div>
      <div className="bg-decoration bg-decoration-2"></div>

      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h1>AI Presentation Evaluator</h1>
            <p>Get instant, AI-powered feedback to improve your presentation skills and deliver with confidence</p>
            <div className="hero-cta">
              <Link to="/upload" className="primary-button">
                Upload Your Presentation
                <ArrowRight size={18} />
              </Link>
            </div>
          </div>
          <div className="hero-image">
            <div className="hero-shape-1"></div>
            <div className="hero-shape-2"></div>
          </div>
        </div>
      </section>

      <section className="features-section">
        <div className="container">
          <div className="section-header">
            <h2>Comprehensive Analysis</h2>
            <p>Our AI evaluates multiple aspects of your presentation to provide holistic feedback</p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <BarChart2 size={32} />
              </div>
              <h3>Content Analysis</h3>
              <p>
                Analyze the quality, structure, and coherence of your presentation content with advanced AI algorithms
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Mic size={32} />
              </div>
              <h3>Speech Analysis</h3>
              <p>Evaluate your speech clarity, pace, tone, and vocal delivery for maximum audience engagement</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Video size={32} />
              </div>
              <h3>Body Language</h3>
              <p>Review your body motion, gestures, posture, and stage presence to enhance your physical delivery</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Smile size={32} />
              </div>
              <h3>Facial Expressions</h3>
              <p>
                Analyze your facial expressions, engagement, and emotional connection to build rapport with your audience
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <div className="container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>Three simple steps to improve your presentation skills</p>
          </div>

          <div className="steps-container">
            <div className="step-item">
              <div className="step-number">1</div>
              <h3>Upload</h3>
              <p>Upload your presentation video or provide a link to your recording in seconds</p>
            </div>

            <div className="step-connector"></div>

            <div className="step-item">
              <div className="step-number">2</div>
              <h3>Analyze</h3>
              <p>Our AI analyzes multiple aspects of your presentation using advanced algorithms</p>
            </div>

            <div className="step-connector"></div>

            <div className="step-item">
              <div className="step-number">3</div>
              <h3>Improve</h3>
              <p>Receive detailed feedback and actionable suggestions to enhance your skills</p>
            </div>
          </div>

          <div className="cta-container">
            <Link to="/upload" className="primary-button">
              Start Your Analysis
              <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>

      <section className="benefits-section">
        <div className="container">
          <div className="section-header">
            <h2>Why Use Our AI Presentation Evaluator?</h2>
            <p>Powerful benefits to help you become a better presenter</p>
          </div>

          <div className="benefits-grid">
            <div className="benefit-item">
              <div className="benefit-icon">
                <CheckCircle size={24} />
              </div>
              <div className="benefit-content">
                <h4>Objective Feedback</h4>
                <p>Receive unbiased, data-driven insights about your presentation style and content.</p>
              </div>
            </div>

            <div className="benefit-item">
              <div className="benefit-icon">
                <CheckCircle size={24} />
              </div>
              <div className="benefit-content">
                <h4>Actionable Improvements</h4>
                <p>Get specific suggestions to enhance your delivery and engage your audience better.</p>
              </div>
            </div>

            <div className="benefit-item">
              <div className="benefit-icon">
                <Award size={24} />
              </div>
              <div className="benefit-content">
                <h4>Track Progress</h4>
                <p>Monitor your improvement over time with detailed analytics and progress tracking.</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section className="final-cta">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Improve Your Presentation Skills?</h2>
            <p>Transform your presenting abilities with AI-powered feedback and actionable insights</p>
            <Link to="/upload" className="primary-button">
              Get Started Now
              <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage