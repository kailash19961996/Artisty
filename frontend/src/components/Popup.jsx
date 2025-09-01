import React, { useEffect } from 'react';
import './Popup.css';

const Popup = ({ isOpen, artwork, onClose }) => {
  // Handle ESC key to close popup
  useEffect(() => {
    if (!isOpen) return;
    
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEsc);
    // Prevent body scroll when popup is open
    document.body.style.overflow = 'hidden';
    
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);
  
  if (!isOpen || !artwork) return null;

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div className="popup-content" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <button 
          className="popup-close"
          onClick={onClose}
          aria-label="Close popup"
        >
          ×
        </button>
        
        <div className="popup-image-container">
          <img
            src={new URL(`../assets/images/${artwork.image}`, import.meta.url).href}
            alt={artwork.name}
            className="popup-image"
          />
        </div>
        
        <div className="popup-details">
          <h2 className="popup-title">{artwork.name}</h2>
          <p className="popup-origin">{artwork.origin}</p>
          <p className="popup-description">{artwork.description}</p>
          <div className="popup-footer">
            <p className="popup-price">{formatPrice(artwork.price)}</p>
            <button className="popup-add-to-cart">
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Popup;