import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Footer from './components/Footer';
import ChatBot from './components/ChatBot';
import ArtCard from './components/ArtCard';
import { artPieces, searchArtPieces } from './data/artData';

function App() {
  const [displayedArt, setDisplayedArt] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const itemsPerPage = 65;

  // Initialize with first batch of art pieces
  useEffect(() => {
    setDisplayedArt(artPieces.slice(0, itemsPerPage));
    setHasMore(artPieces.length > itemsPerPage);
  }, []);

  const handleSearch = (query) => {
    setSearchQuery(query);
    setLoading(true);
    setCurrentPage(0);

    // Simulate loading delay for better UX
    setTimeout(() => {
      if (query.trim() === '') {
        // Show all art pieces
        setDisplayedArt(artPieces.slice(0, itemsPerPage));
        setHasMore(artPieces.length > itemsPerPage);
      } else {
        // Show search results
        const results = searchArtPieces(query);
        setDisplayedArt(results.slice(0, itemsPerPage));
        setHasMore(results.length > itemsPerPage);
      }
      setLoading(false);
    }, 500);
  };

  const loadMore = () => {
    setLoading(true);
    const nextPage = currentPage + 1;
    const startIndex = nextPage * itemsPerPage;

    setTimeout(() => {
      let sourceData;
      if (searchQuery.trim() === '') {
        sourceData = artPieces;
      } else {
        sourceData = searchArtPieces(searchQuery);
      }

      const newItems = sourceData.slice(startIndex, startIndex + itemsPerPage);
      setDisplayedArt(prev => [...prev, ...newItems]);
      setCurrentPage(nextPage);
      setHasMore(startIndex + itemsPerPage < sourceData.length);
      setLoading(false);
    }, 500);
  };

  return (
    <div className="app-container">
      <Header />
      
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <h1 className="hero-title">
            Discover <span className="hero-title-highlight">Extraordinary</span>
            <span className="hero-title-block">Art Collection</span>
          </h1>
          <p className="hero-description">
            Explore our curated selection of stunning artworks from talented artists around the world.
            Find the perfect piece to transform your space.
          </p>
          
          {/* Large Search Bar */}
          <div className="hero-search-container">
            <SearchBar onSearch={handleSearch} />
          </div>
          
          {/* Modern Stats Section */}
          <div className="stats-section">
            <div className="stat-item">
              <div className="stat-number">60+</div>
              <div className="stat-label">Curated Artworks</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">30+</div>
              <div className="stat-label">Countries Represented</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">100%</div>
              <div className="stat-label">Authenticity Guaranteed</div>
            </div>
          </div>
        </div>
      </section>

      {/* Gallery Section */}
      <section className="gallery-section">
        <div className="gallery-container">
          <div className="gallery-header">
            <h2 className="gallery-title">Our Art Collection</h2>
            <p className="gallery-description">
              {searchQuery ? `Search results for "${searchQuery}"` : 'Browse our carefully curated selection of extraordinary artworks'}
            </p>
          </div>
          
          <div className="gallery-grid">
            {displayedArt.map((art) => (
              <ArtCard key={art.id} art={art} />
            ))}
          </div>
          
          {hasMore && !loading && (
            <div className="load-more-container">
              <button
                onClick={loadMore}
                className="load-more-button"
              >
                Load More Artworks
              </button>
            </div>
          )}
        </div>
      </section>

      <Footer />
      <ChatBot />
    </div>
  );
}

export default App;