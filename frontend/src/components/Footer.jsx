import React from 'react';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        {/* Main Content */}
        <div className="footer-main">
          <div className="footer-logo">
            <div className="footer-logo-icon">
              <span>🎨</span>
            </div>
            <span className="footer-logo-text">Artisty</span>
          </div>
          <p className="footer-description">
            Built by Kai, find more @ www.kailash.london
          </p>
        </div>

        {/* Bottom Section */}
        <div className="footer-bottom">
          <p className="footer-copyright">© 2024 Artisty. All rights reserved.</p>
          <div className="footer-links">
            <a href="#terms" className="footer-link">Terms</a>
            <a href="#privacy" className="footer-link">Privacy</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
