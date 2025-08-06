import React from 'react';
import ArtCard from './ArtCard';

const ArtGrid = ({ artPieces, loading = false }) => {
  if (loading) {
    return (
      <div className="art-grid-loading">
        {[...Array(8)].map((_, index) => (
          <div key={index} className="art-grid-loading-card">
            <div className="art-grid-loading-image"></div>
            <div className="art-grid-loading-content">
              <div className="art-grid-loading-title"></div>
              <div className="art-grid-loading-description"></div>
              <div className="art-grid-loading-footer">
                <div className="art-grid-loading-price"></div>
                <div className="art-grid-loading-button"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!artPieces || artPieces.length === 0) {
    return (
      <div className="art-grid-empty">
        <svg className="art-grid-empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="art-grid-empty-title">No artworks found</h3>
        <p className="art-grid-empty-description">Try adjusting your search criteria or browse all artworks.</p>
      </div>
    );
  }

  return (
    <div className="art-grid">
      {artPieces.map((art) => (
        <ArtCard key={art.id} art={art} />
      ))}
    </div>
  );
};

export default ArtGrid;