import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import '../../styles/Sidebar.css'; // You'll need to create this CSS file

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const location = useLocation();
  
  // Define sidebar navigation items
  const navItems = [
    { 
      path: '/', 
      label: 'Dashboard', 
      icon: '📊',
      exact: true 
    },
    { 
      path: '/upload', 
      label: 'Upload Video', 
      icon: '📤' 
    },
    { 
      path: '/analysis', 
      label: 'Analysis Results', 
      icon: '📝' 
    },
    { 
      path: '/history', 
      label: 'History', 
      icon: '📚' 
    },
    { 
      path: '/profile', 
      label: 'Profile', 
      icon: '👤' 
    }
  ];
  
  // Analysis sub-menu items that appear when viewing analysis results
  const analysisSubItems = [
    {
      path: '/analysis/motion',
      label: 'Motion Analysis',
      icon: '🏃'
    },
    {
      path: '/analysis/expression',
      label: 'Expression Analysis',
      icon: '😀'
    },
    {
      path: '/analysis/audio',
      label: 'Audio Analysis',
      icon: '🔊'
    },
    {
      path: '/analysis/content',
      label: 'Content Analysis',
      icon: '📝'
    },
    {
      path: '/analysis/disfluency',
      label: 'Disfluency Analysis',
      icon: '🗣️'
    }
  ];
  
  // Check if we're on any analysis page to show sub-menu
  const isAnalysisPage = location.pathname.startsWith('/analysis');
  
  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <h2>Menu</h2>
        <button className="close-sidebar" onClick={toggleSidebar} aria-label="Close sidebar">
          &times;
        </button>
      </div>
      
      <nav className="sidebar-nav">
        <ul className="nav-list">
          {navItems.map((item) => (
            <li key={item.path} className={location.pathname === item.path ? 'active' : ''}>
              <NavLink 
                to={item.path} 
                exact={item.exact ? "true" : undefined}
                className={({ isActive }) => isActive ? 'active' : ''}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
        
        {/* Show analysis sub-menu when on analysis pages */}
        {isAnalysisPage && (
          <div className="sub-menu">
            <h3>Analysis Details</h3>
            <ul className="nav-list sub-nav-list">
              {analysisSubItems.map((item) => (
                <li key={item.path} className={location.pathname === item.path ? 'active' : ''}>
                  <NavLink 
                    to={item.path}
                    className={({ isActive }) => isActive ? 'active' : ''}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    <span className="nav-label">{item.label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        )}
      </nav>
      
      <div className="sidebar-footer">
        <a href="https://github.com/yourusername/presentation-evaluator" 
           target="_blank" 
           rel="noopener noreferrer"
           className="github-link">
          <span className="nav-icon">📂</span>
          <span className="nav-label">GitHub Repository</span>
        </a>
      </div>
    </aside>
  );
};

export default Sidebar;