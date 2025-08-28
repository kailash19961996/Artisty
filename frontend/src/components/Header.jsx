import React from 'react';

const Header = () => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="header-content">
          {/* Logo */}
          <div className="header-logo">
            <div className="header-logo-icon">
              <span>🎨</span>
            </div>
            <span className="header-logo-text">Artisty</span>
          </div>

          {/* Right Side Actions */}
          <div className="header-actions">
            {/* Globe Icon */}
            <button className="header-globe-btn">
              <svg className="header-globe-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 919-9" />
              </svg>
            </button>

            {/* Menu Button */}
            <button className="header-menu-btn">
              Menu
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;