import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Import global styles
import './styles/global.css';

// Common components
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import Sidebar from './components/common/Sidebar';

// Original components (for backward compatibility)
import SummaryDashboard from './components/analysis/SummaryDashboard';
import VideoUploader from './components/video/VideoUploader';
import MotionAnalysisResults from './components/analysis/MotionAnalysisResults';

// New page components - create placeholders if not implemented yet
const HomePage = () => <SummaryDashboard />; // Use your existing dashboard as homepage for now
const UploadPage = () => <VideoUploader />; // Use your existing uploader
const AnalysisPage = () => <MotionAnalysisResults />; // Use your existing results page

// Placeholder pages - replace these with actual implementations when ready
const HistoryPage = () => (
  <div className="container">
    <h1>Analysis History</h1>
    <p>Your previous analysis sessions will appear here.</p>
  </div>
);

const ProfilePage = () => (
  <div className="container">
    <h1>User Profile</h1>
    <p>User profile settings will appear here.</p>
  </div>
);

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Router>
      <div className="app-container">
        <Header toggleSidebar={toggleSidebar} />
        <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} />
        
        <main className={`main-content ${sidebarOpen ? 'with-sidebar' : ''}`}>
          <Routes>
            {/* New routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/analysis/*" element={<AnalysisPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            
            {/* Legacy routes with redirects to maintain compatibility */}
            <Route path="/summary" element={<Navigate to="/" replace />} />
            <Route path="/analysis-results" element={<Navigate to="/analysis" replace />} />
          </Routes>
        </main>
        
        <Footer />
      </div>
    </Router>
  );
}

export default App;