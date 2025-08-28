import React, { useState } from 'react';

const SearchBar = ({ onSearch, placeholder = "Search artworks by name, description, or origin..." }) => {
  const [query, setQuery] = useState('');

  const scrollToResults = () => {
    setTimeout(() => {
      const gallerySection = document.getElementById('art-collection') ||
        document.querySelector('.gallery-section') ||
        document.querySelector('.gallery-container') ||
        document.querySelector('.gallery-header');
      if (gallerySection) {
        gallerySection.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' });
      } else {
        window.scrollBy({ top: 600, behavior: 'smooth' });
      }
    }, 800);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
    scrollToResults();
  };

  const handleChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    // Real-time search
    onSearch(value);
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-wrapper">
          <div className="search-icon-wrapper">
            <svg className="search-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
            </svg>
          </div>
          <input
            type="text"
            value={query}
            onChange={handleChange}
            className="search-input"
            placeholder={placeholder}
          />
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                onSearch('');
              }}
              className="search-clear-btn"
            >
              <svg className="search-clear-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default SearchBar;