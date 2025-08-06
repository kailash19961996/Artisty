import React from 'react';
import ArtCard from './ArtCard';

const ArtGrid = ({ artPieces, loading = false }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 animate-fade-in">
        {[...Array(8)].map((_, index) => (
          <div key={index} className="card">
            <div className="w-full h-64 bg-gray-200 animate-pulse"></div>
            <div className="p-6">
              <div className="h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="h-3 bg-gray-200 rounded animate-pulse mb-4 w-3/4"></div>
              <div className="flex justify-between items-center">
                <div className="h-6 bg-gray-200 rounded animate-pulse w-20"></div>
                <div className="h-8 bg-gray-200 rounded animate-pulse w-24"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!artPieces || artPieces.length === 0) {
    return (
      <div className="text-center py-16">
        <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 className="text-xl font-semibold text-gray-600 mb-2">No artworks found</h3>
        <p className="text-gray-500">Try adjusting your search criteria or browse all artworks.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 animate-fade-in">
      {artPieces.map((art) => (
        <ArtCard key={art.id} art={art} />
      ))}
    </div>
  );
};

export default ArtGrid;