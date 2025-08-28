import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Footer from './components/Footer';
import ChatBot from './components/ChatBot';
import ArtCard from './components/ArtCard';
import Banner from './components/Banner';
import { artPieces, searchArtPieces, semanticSearchArtPieces } from './data/artData';
import StatCounter from './components/StatCounter';

function App() {
  const [displayedArt, setDisplayedArt] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const itemsPerPage = 65;
  useEffect(() => {
    setDisplayedArt(artPieces.slice(0, itemsPerPage));
    setHasMore(artPieces.length > itemsPerPage);
  }, []);
  useEffect(() => {
    const handleAgentSearch = (event) => {
      const { searchTerm } = event.detail;
      console.log('Agent triggered search:', searchTerm);
      handleSearch(searchTerm);
    };

    window.addEventListener('agentSearch', handleAgentSearch);
    return () => window.removeEventListener('agentSearch', handleAgentSearch);
  }, []);

  const handleSearch = (query) => {
    setSearchQuery(query);
    setLoading(true);
    setCurrentPage(0);
    setTimeout(() => {
      if (query.trim() === '') {
        setDisplayedArt(artPieces.slice(0, itemsPerPage));
        setHasMore(artPieces.length > itemsPerPage);
      } else {
        const tokens = query.trim().split(/\s+/);
        let explicitSelection = [];
        if (tokens.length >= 2) {
          const pairs = [];
          for (let i = 0; i + 1 < tokens.length; i += 2) {
            pairs.push(`${tokens[i]} ${tokens[i+1]}`.toLowerCase());
          }
          const byName = new Map(artPieces.map(a => [a.name.toLowerCase(), a]));
          explicitSelection = pairs.map(p => byName.get(p)).filter(Boolean);
        }

        if (explicitSelection.length > 0) {
          setDisplayedArt(explicitSelection.slice(0, itemsPerPage));
          setHasMore(false);
        } else {
          const semanticTop = semanticSearchArtPieces(query, 5);
          const keywordResults = searchArtPieces(query);
          const combined = [...semanticTop];
          keywordResults.forEach(k => {
            if (!combined.some(a => a.id === k.id)) combined.push(k);
          });
          setDisplayedArt(combined.slice(0, itemsPerPage));
          setHasMore(combined.length > itemsPerPage);
        }
      }
      setLoading(false);
    }, 600);
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
    <div className={`app-container ${isChatOpen ? 'chat-open' : ''}`}>
      <Banner />
      <div className="main-content">
        <Header />

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
          
          <div className="stats-section">
            <div className="stat-item">
              <div className="stat-number"><StatCounter target={60} suffix="+" durationMs={1200} /></div>
              <div className="stat-label">Curated Artworks</div>
            </div>
            <div className="stat-item">
              <div className="stat-number"><StatCounter target={30} suffix="+" durationMs={1200} /></div>
              <div className="stat-label">Countries Represented</div>
            </div>
            <div className="stat-item">
              <div className="stat-number"><StatCounter target={100} suffix="%" durationMs={1400} /></div>
              <div className="stat-label">Authenticity Guaranteed</div>
            </div>
          </div>
        </div>
      </section>
      <section id="art-collection" className="gallery-section">
        <div className="gallery-container">

          <div className="gallery-search-container">
            <SearchBar onSearch={handleSearch} />
          </div>
          <div className="gallery-header">
            <h2 className="gallery-title">Our Art Collection</h2>
            <p 
              className="gallery-description" 
              data-search-results={searchQuery ? 'true' : 'false'}
            >
              {searchQuery ? `Search results for "${searchQuery}"` : 'Browse our carefully curated selection of extraordinary artworks'}
            </p>
          </div>
          
          {loading ? (
            <div className="gallery-loading">
              <div className="spinner" />
              <p className="loading-text">Finding beautiful pieces...</p>
            </div>
          ) : (
            <div className="gallery-grid">
              {displayedArt.map((art) => (
                <ArtCard key={art.id} art={art} />
              ))}
            </div>
          )}
          
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
      </div>
      
      <ChatBot 
        isOpen={isChatOpen} 
        onToggle={() => setIsChatOpen(!isChatOpen)} 
      />
    </div>
  );
}

export default App;