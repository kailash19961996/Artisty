import React from 'react';
import './Header.css';

const Header = ({ onCartClick, cartCount = 0 }) => {
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
            {/* Cart Icon with badge - no background */}
            <button onClick={onCartClick} className="header-cart-btn">
              <svg className="header-cart-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l3-8H6.4M7 13L5.4 5M7 13l-2 9m12-9l2 9M9 21a1 1 0 100-2 1 1 0 000 2zm8 0a1 1 0 100-2 1 1 0 000 2z" />
              </svg>
              <span id="cart-badge" className="header-cart-badge" hidden={cartCount === 0}>{cartCount}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;