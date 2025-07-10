import React from "react"
import { Link } from "react-router-dom"
import "../styles/HomePage.css"
import { analysisService } from '../services/analysisService'
import { 
  ArrowRight, 
  Mic, 
  Video, 
  BarChart2, 
  Smile, 
  Award, 
  Clock, 
  Play,
  Users,
  TrendingUp,
  Shield,
  Upload,
  Star
} from "lucide-react"

const HomePage = () => {
  const features = [
    {
      icon: <BarChart2 size={28} />,
      title: "Content Analysis",
      description: "Analyze the quality, structure, and coherence of your presentation content with advanced AI algorithms.",
      color: "blue"
    },
    {
      icon: <Video size={28} />,
      title: "Body Language",
      description: "Get insights on your posture, gestures, and movement to improve your physical presence.",
      color: "green"
    },
    {
      icon: <Mic size={28} />,
      title: "Speech Analysis",
      description: "Evaluate your speaking pace, clarity, volume, and detect filler words automatically.",
      color: "purple"
    },
    {
      icon: <Smile size={28} />,
      title: "Facial Expression",
      description: "Understand your emotional engagement and facial expressions throughout your presentation.",
      color: "orange"
    }
  ]

  const stats = [
    { number: "10,000+", label: "Presentations Analyzed", icon: <BarChart2 size={20} /> },
    { number: "95%", label: "Improvement Rate", icon: <TrendingUp size={20} /> },
    { number: "500+", label: "Happy Users", icon: <Users size={20} /> },
    { number: "4.9/5", label: "Average Rating", icon: <Star size={20} /> }
  ]

  const benefits = [
    {
      icon: <Clock size={24} />,
      title: "Save Time",
      description: "Get instant feedback instead of waiting for human reviewers"
    },
    {
      icon: <Award size={24} />,
      title: "Improve Skills",
      description: "Detailed analytics help you identify and fix specific issues"
    },
    {
      icon: <Shield size={24} />,
      title: "Private & Secure",
      description: "Your videos are processed securely and never stored permanently"
    }
  ]

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Perfect Your Presentation Skills with AI Feedback
          </h1>
          <p className="hero-subtitle">
            Get instant, comprehensive analysis of your presentation skills including speech patterns, 
            body language, facial expressions, and content quality. Improve with confidence.
          </p>
          <div className="hero-cta">
            <Link to="/upload" className="btn btn-primary btn-lg">
              <Upload size={20} />
              Start Free Analysis
              <ArrowRight size={18} />
            </Link>
            <button className="btn btn-secondary btn-lg">
              <Play size={20} />
              Watch Demo
            </button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <div className="stat-number">{stat.number}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">
                {feature.icon}
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Benefits Section */}
      <section className="stats-section">
        <div className="stats-grid">
          {benefits.map((benefit, index) => (
            <div key={index} className="stat-card">
              <div className="feature-icon">
                {benefit.icon}
              </div>
              <h3 className="feature-title">{benefit.title}</h3>
              <p className="feature-description">{benefit.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Improve Your Presentations?</h2>
          <p className="cta-subtitle">Upload your first video and get detailed AI feedback in minutes</p>
          <Link to="/upload" className="cta-button">
            Get Started Free
            <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* API Status Section - temporary for debugging */}
      <section className="stats-section">
        <div className="container">
          <div className="text-center mb-8">
            <h3 className="text-xl font-semibold mb-4">API Status</h3>
            <button 
              className="btn btn-secondary"
              onClick={async () => {
                try {
                  const response = await analysisService.testConnection();
                  alert('API Connection Successful!\n' + JSON.stringify(response.data, null, 2));
                } catch (error) {
                  alert('API Connection Failed:\n' + error.message);
                }
              }}
            >
              Test API Connection
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
