import React, { useState, useEffect } from "react"
import { Link, useLocation } from "react-router-dom"
import { Menu, X, Home, Upload, BarChart3, Sparkles } from "lucide-react"
import "../../styles/Header.css"

const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const location = useLocation()

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const toggleMenu = () => {
    setMenuOpen(!menuOpen)
  }

  // Close menu when clicking outside or on route change
  useEffect(() => {
    setMenuOpen(false)
  }, [location.pathname])

  useEffect(() => {
    const closeMenu = (e) => {
      if (menuOpen && !e.target.closest('.header-container')) {
        setMenuOpen(false)
      }
    }

    document.addEventListener("click", closeMenu)
    return () => document.removeEventListener("click", closeMenu)
  }, [menuOpen])

  const navItems = [
    {
      path: "/",
      label: "Home",
      icon: <Home size={18} />
    },
    {
      path: "/upload",
      label: "Upload Video",
      icon: <Upload size={18} />
    },
    {
      path: "/analysis",
      label: "Analysis",
      icon: <BarChart3 size={18} />
    }
  ]

  return (
    <header className={`app-header ${scrolled ? "scrolled" : ""}`}>
      <div className="header-container">
        {/* Logo/Brand */}
        <Link to="/" className="header-brand">
          <div className="brand-icon">
            <Sparkles size={24} />
          </div>
          <span className="brand-text">AI Presenter</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="desktop-nav">
          <ul>
            {navItems.map((item) => (
              <li key={item.path} className={location.pathname === item.path ? "active" : ""}>
                <Link to={item.path} className="nav-link">
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-btn"
          onClick={toggleMenu}
          aria-label="Toggle menu"
          aria-expanded={menuOpen}
        >
          {menuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Mobile Navigation */}
        <nav className={`mobile-nav ${menuOpen ? "open" : ""}`}>
          <ul>
            {navItems.map((item) => (
              <li key={item.path} className={location.pathname === item.path ? "active" : ""}>
                <Link to={item.path} className="nav-link">
                  {item.icon}
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  )
}

export default Header