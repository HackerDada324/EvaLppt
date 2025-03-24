import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../../styles/Header.css'; // You'll need to create this CSS file

const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  
  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  return (
    <header className="app-header">
      <div className="header-container">
        <div className="logo-container">
          <Link to="/" className="logo">
            <img src="/assets/logo.png" alt="Presentation Evaluator" />
            <span>Presentation Evaluator</span>
          </Link>
        </div>

        <nav className={`main-nav ${menuOpen ? 'open' : ''}`}>
          <ul>
            <li className={location.pathname === '/' ? 'active' : ''}>
              <Link to="/">Home</Link>
            </li>
            <li className={location.pathname === '/upload' ? 'active' : ''}>
              <Link to="/upload">New Analysis</Link>
            </li>
            <li className={location.pathname === '/history' ? 'active' : ''}>
              <Link to="/history">History</Link>
            </li>
            <li className={location.pathname === '/profile' ? 'active' : ''}>
              <Link to="/profile">Profile</Link>
            </li>
          </ul>
        </nav>

        <div className="header-actions">
          {/* If you have authentication, you can add user menu here */}
          <button className="primary-button">
            <Link to="/upload">Analyze Presentation</Link>
          </button>
          
          <button className="mobile-menu-toggle" onClick={toggleMenu} aria-label="Toggle menu">
            <span className="hamburger-icon"></span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;