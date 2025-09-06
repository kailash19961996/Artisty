/**
 * ARTISTY - Main Application Component
 * 
 * This is the root component for the Artisty art gallery application.
 * It manages the entire application state and coordinates between different views:
 * - Gallery view with art collection browsing
 * - Cart view for shopping cart management
 * - AI-powered chatbot integration with real-time actions
 * 
 * Key Features:
 * - Agentic AI chatbot that can control UI (search, cart, navigation, popups)
 * - Intelligent search combining semantic AI search with keyword filtering
 * - Real-time cart management with visual feedback animations
 * - Responsive layout that adapts when chatbot is open (70% content, 30% chat)
 * - Event-driven architecture for AI agent communication
 * 
 * Architecture:
 * - Uses custom events for AI agent communication (agentSearch, agentQuickView, etc.)
 * - Implements dual search strategy: explicit artwork matching + semantic/keyword search
 * - Manages cart state with visual feedback (animations, badges, floating stars)
 * - Coordinates between gallery and cart views seamlessly
 * 
 * @author Artisty Team
 * @version 2.1.0 - Added AI agent integration with direct JSON responses
 */

import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Footer from './components/Footer';
import ChatBot from './components/ChatBot';
import ArtCard from './components/ArtCard';
import Banner from './components/Banner';
import { artPieces, searchArtPieces, semanticSearchArtPieces } from './data/artData';
import StatCounter from './components/StatCounter';
import CartPage from './components/CartPage';
import Popup from './components/Popup';

function App() {
  // === STATE MANAGEMENT ===
  
  // Gallery & Search State
  const [displayedArt, setDisplayedArt] = useState([]); // Currently displayed artworks
  const [searchQuery, setSearchQuery] = useState(''); // Current search query
  const [loading, setLoading] = useState(false); // Loading state for search operations
  const [currentPage, setCurrentPage] = useState(0); // Pagination state
  const [hasMore, setHasMore] = useState(true); // Whether more artworks can be loaded
  
  // Shopping Cart State
  const [cart, setCart] = useState([]); // Shopping cart items
  
  // UI State Management
  const [isChatOpen, setIsChatOpen] = useState(false); // Chatbot visibility
  const [currentView, setCurrentView] = useState('gallery'); // 'gallery' | 'cart'
  const [popupArtwork, setPopupArtwork] = useState(null); // Artwork for quick-view popup
  
  // Configuration
  const itemsPerPage = 65; // Number of items per page for pagination
  // === INITIALIZATION ===
  // Load initial artwork collection on component mount
  useEffect(() => {
    setDisplayedArt(artPieces.slice(0, itemsPerPage));
    setHasMore(artPieces.length > itemsPerPage);
  }, []);

  // === AI AGENT EVENT HANDLERS ===
  // This effect sets up event listeners for AI agent actions
  // The chatbot can trigger various UI actions through custom events
  useEffect(() => {
    /**
     * Handle search requests from AI agent
     * Triggered when agent suggests artworks or user asks to search
     */
    const handleAgentSearch = (event) => {
      const { searchTerm } = event.detail;
      console.log('Agent triggered search:', searchTerm);
      handleSearch(searchTerm);
    };
    
    const handleAgentQuickView = (event) => {
      const { artworkName } = event.detail;
      console.log('[DEBUG] Agent quick view for:', artworkName);
      
      // Find artwork and open popup directly
      const artwork = displayedArt.find(art => 
        art.name.toLowerCase().includes(artworkName.toLowerCase()) ||
        artworkName.toLowerCase().includes(art.name.toLowerCase())
      );
      
      console.log('[DEBUG] Found artwork:', artwork);
      
      if (artwork) {
        setPopupArtwork(artwork);
        console.log('[DEBUG] Opened popup for:', artwork.name);
      } else {
        console.log('[DEBUG] Artwork not found for quick view:', artworkName);
      }
    };
    
    const handleAgentAddToCart = (event) => {
      const { artworkName } = event.detail;
      console.log('[DEBUG] Agent add to cart for:', artworkName);
      
      // Find artwork and add to cart
      const artwork = displayedArt.find(art => 
        art.name.toLowerCase().includes(artworkName.toLowerCase()) ||
        artworkName.toLowerCase().includes(art.name.toLowerCase())
      );
      
      console.log('[DEBUG] Found artwork for cart:', artwork);
      
      if (artwork) {
        addToCart(artwork);
        console.log('[DEBUG] Added to cart:', artwork.name);
        
        // Also trigger the visual feedback on the art card button
        window.dispatchEvent(new CustomEvent('triggerAddToCartFeedback', { 
          detail: { artworkId: artwork.id } 
        }));
      } else {
        console.log('[DEBUG] Artwork not found for add to cart:', artworkName);
      }
    };
    
    const handleAgentNavigate = (event) => {
      const { destination } = event.detail;
      console.log('[DEBUG] Agent navigate to:', destination);
      
      if (destination === 'cart') {
        setCurrentView('cart');
        console.log('[DEBUG] Navigated to cart view');
      } else if (destination === 'home') {
        setCurrentView('gallery');
        console.log('[DEBUG] Navigated to gallery view');
      }
    };
    
    const handleAgentCheckout = () => {
      console.log('[DEBUG] Agent checkout triggered');
      setCurrentView('cart');
      // Trigger checkout modal after a brief delay
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('triggerCheckout'));
        console.log('[DEBUG] Dispatched triggerCheckout event');
      }, 500);
    };

    window.addEventListener('agentSearch', handleAgentSearch);
    window.addEventListener('agentQuickView', handleAgentQuickView);
    window.addEventListener('agentAddToCart', handleAgentAddToCart);
    window.addEventListener('agentNavigate', handleAgentNavigate);
    window.addEventListener('agentCheckout', handleAgentCheckout);
    
    return () => {
      window.removeEventListener('agentSearch', handleAgentSearch);
      window.removeEventListener('agentQuickView', handleAgentQuickView);
      window.removeEventListener('agentAddToCart', handleAgentAddToCart);
      window.removeEventListener('agentNavigate', handleAgentNavigate);
      window.removeEventListener('agentCheckout', handleAgentCheckout);
    };
  }, [displayedArt]);

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

  // Cart helpers
  const addToCart = (item) => {
    setCart((prev) => {
      const updated = [...prev, item];
      const badge = document.getElementById('cart-badge');
      const cartBtn = document.querySelector('.header-cart-btn');
      
      if (badge) {
        badge.textContent = String(updated.length);
        badge.hidden = updated.length === 0;
        badge.classList.remove('pulse');
        // trigger reflow then add
        void badge.offsetWidth;
        badge.classList.add('pulse');
      }
      
      if (cartBtn) {
        // Add shake and sparkle effects
        cartBtn.classList.remove('shake', 'sparkle');
        void cartBtn.offsetWidth; // trigger reflow
        cartBtn.classList.add('shake', 'sparkle');
        
        // Add additional floating stars
        const createFloatingStar = (delay = 0) => {
          const star = document.createElement('span');
          star.innerHTML = '★';
          star.style.cssText = `
            position: absolute;
            font-size: 8px;
            color: #8b5cf6;
            text-shadow: 0 0 6px rgba(139, 92, 246, 0.8);
            pointer-events: none;
            z-index: 15;
            opacity: 0;
            top: ${Math.random() * 20 - 10}px;
            left: ${Math.random() * 20 - 10}px;
            animation: floatingStar 1s ease ${delay}ms;
          `;
          cartBtn.appendChild(star);
          
          setTimeout(() => {
            if (star.parentNode) star.parentNode.removeChild(star);
          }, 1000 + delay);
        };
        
        // Create 3 floating stars with delays
        createFloatingStar(0);
        createFloatingStar(200);
        createFloatingStar(400);
        
        // Remove effects after animation completes
        setTimeout(() => {
          cartBtn.classList.remove('shake', 'sparkle');
        }, 1200);
      }
      
      // Persist "added" state for matching ArtCard buttons
      window.dispatchEvent(new CustomEvent('triggerAddToCartFeedback', { 
        detail: { artworkId: item.id }
      }));
      return updated;
    });
  };

  const removeFromCart = (itemId) => {
    setCart((prev) => {
      const itemIndex = prev.findIndex(item => item.id === itemId);
      if (itemIndex >= 0) {
        const updated = [...prev];
        updated.splice(itemIndex, 1);
        const badge = document.getElementById('cart-badge');
        if (badge) {
          badge.textContent = String(updated.length);
          badge.hidden = updated.length === 0;
        }
        return updated;
      }
      return prev;
    });
  };

  const goToCart = () => setCurrentView('cart');
  const goToGallery = () => setCurrentView('gallery');

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

  if (currentView === 'cart') {
    return (
      <div className={`app-container ${isChatOpen ? 'chat-open' : ''}`}>
        <CartPage 
          cart={cart} 
          onRemoveFromCart={removeFromCart}
          onGoBack={goToGallery}
        />
        <ChatBot 
          isOpen={isChatOpen} 
          onToggle={() => setIsChatOpen(!isChatOpen)} 
        />
      </div>
    );
  }

  return (
    <div className={`app-container ${isChatOpen ? 'chat-open' : ''}`}>
      <div className="main-content">
        <Header onCartClick={goToCart} cartCount={cart.length} />

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
      <Banner />
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
                <ArtCard 
                  key={art.id} 
                  art={art} 
                  onAddToCart={() => addToCart(art)}
                  onQuickView={() => setPopupArtwork(art)}
                />
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
      
      <Popup 
        isOpen={!!popupArtwork}
        artwork={popupArtwork}
        onClose={() => setPopupArtwork(null)}
        onAddToCart={() => popupArtwork && addToCart(popupArtwork)}
      />
    </div>
  );
}

export default App;