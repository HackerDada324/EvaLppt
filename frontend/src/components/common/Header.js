"use client"

import { useState, useEffect } from "react"
import { Link, useLocation } from "react-router-dom"
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

  // Close menu when clicking outside
  useEffect(() => {
    const closeMenu = () => {
      if (menuOpen) setMenuOpen(false)
    }

    document.body.addEventListener("click", closeMenu)
    return () => document.body.removeEventListener("click", closeMenu)
  }, [menuOpen])

  return (
    <header className={`app-header ${scrolled ? "scrolled" : ""}`}>
      <div className="header-container">
        <div className="logo-container">
          <Link to="/" className="logo">
            <span>DataAnalyzer</span>
          </Link>
        </div>

        <nav className={`main-nav ${menuOpen ? "open" : ""}`} onClick={(e) => e.stopPropagation()}>
          <ul>
            <li className={location.pathname === "/" ? "active" : ""}>
              <Link to="/">Home</Link>
            </li>
            <li className={location.pathname === "/upload" ? "active" : ""}>
              <Link to="/upload">New Analysis</Link>
            </li>
          </ul>
        </nav>

        <div className="header-actions">
          <button className="primary-button">
            <Link to="/upload">Start Analysis</Link>
          </button>
          <button
            className={`mobile-menu-toggle ${menuOpen ? "open" : ""}`}
            onClick={(e) => {
              e.stopPropagation()
              toggleMenu()
            }}
            aria-label="Toggle menu"
          >
            <span className="hamburger-icon"></span>
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header