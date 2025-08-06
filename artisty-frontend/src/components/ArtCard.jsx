import React, { useState } from 'react';

const ArtCard = ({ art }) => {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

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
            src={`/src/assets/images/${art.image}`}
            alt={art.name}
            className={`art-card-image ${isLoading ? 'loading' : 'loaded'}`}
            onLoad={handleImageLoad}
            onError={handleImageError}
          />
        )}
        
        {/* Overlay with quick view button */}
        <div className="art-card-overlay">
          <button className="art-card-quick-view">
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
          <button className="art-card-button">
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
};

export default ArtCard;