/**
 * ARTISTY ART CARD - Individual Artwork Display Component
 * 
 * Displays individual artwork cards in the gallery with interactive features.
 * Provides visual feedback for user actions and integrates with AI agent events.
 * 
 * Features:
 * - Responsive image loading with error handling
 * - Quick view overlay for artwork details
 * - Add to cart with visual feedback animations
 * - AI agent integration (responds to triggerAddToCartFeedback events)
 * - Price formatting with internationalization
 * - Loading states and error fallbacks
 * 
 * User Interactions:
 * - Hover: Shows quick view overlay
 * - Click Quick View: Opens artwork detail popup
 * - Click Add to Cart: Adds artwork to cart with animation feedback
 * 
 * @param {Object} art - Artwork object with id, name, image, price, origin, description
 * @param {function} onAddToCart - Callback function when artwork is added to cart
 * @param {function} onQuickView - Callback function when quick view is triggered
 * 
 * @author Artisty Team
 * @version 2.0.0 - Added AI agent integration and enhanced feedback
 */

import React, { useState, useEffect } from 'react';
import './ArtCard.css';

const ArtCard = ({ art, onAddToCart, onQuickView }) => {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isAdded, setIsAdded] = useState(false);

  
  useEffect(() => {
    const handleTriggerAddToCartFeedback = (event) => {
      if (event.detail.artworkId === art.id) {
        console.log('[DEBUG] Triggering add to cart feedback for:', art.name);
        setIsAdded(true);
        setTimeout(() => setIsAdded(false), 2000);
      }
    };
    
    window.addEventListener('triggerAddToCartFeedback', handleTriggerAddToCartFeedback);
    
    return () => {
      window.removeEventListener('triggerAddToCartFeedback', handleTriggerAddToCartFeedback);
    };
  }, [art.id]);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const handleImageLoad = () => {
    setIsLoading(false);
  };

  const handleImageError = () => {
    setImageError(true);
    setIsLoading(false);
  };

  return (
    <div className="art-card">
      <div className="art-card-image-container">
        {isLoading && (
          <div className="art-card-loading">
            <svg className="art-card-loading-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
        {imageError ? (
          <div className="art-card-error">
            <div className="art-card-error-content">
              <svg className="art-card-error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p className="art-card-error-text">{art.name}</p>
            </div>
          </div>
        ) : (
          <img
            src={new URL(`../assets/images/${art.image}`, import.meta.url).href}
            alt={art.name}
            className={`art-card-image ${isLoading ? 'loading' : 'loaded'}`}
            onLoad={handleImageLoad}
            onError={handleImageError}
          />
        )}
        
        {/* Overlay with quick view button */}
        <div className="art-card-overlay">
          <button 
            className="art-card-quick-view"
            onClick={onQuickView}
          >
            Quick View
          </button>
        </div>
      </div>

      <div className="art-card-content">
        <div className="art-card-header">
          <h3 className="art-card-title">
            {art.name}
          </h3>
          <span className="art-card-origin">
            {art.origin}
          </span>
        </div>
        
        <p className="art-card-description">
          {art.description}
        </p>
        
        <div className="art-card-footer">
          <span className="art-card-price">
            {formatPrice(art.price)}
          </span>
          <button 
            className={`art-card-button ${isAdded ? 'added' : ''}`}
            onClick={() => {
              if (onAddToCart) onAddToCart();
              setIsAdded(true);
              setTimeout(() => setIsAdded(false), 2000);
            }}
            aria-label={isAdded ? 'Added to Cart' : 'Add to Cart'}
          >
            {isAdded ? (
              <>
                <span>Added to Cart!</span>
                <svg className="cart-check-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </>
            ) : 'Add to Cart'}
          </button>
        </div>
      </div>

    </div>
  );
};

export default ArtCard;