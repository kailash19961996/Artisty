import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Footer from './components/Footer';
import ChatBot from './components/ChatBot';
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
    <div className="min-h-screen">
      <Header />
      
      {/* Hero Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-6xl md:text-8xl font-normal text-black mb-8 tracking-tight">
            Discover <span className="text-[#E7F9E4]">Extraordinary</span>
            <span className="block">Art Collection</span>
          </h1>
          <p className="text-xl text-gray-700 mb-12 max-w-3xl mx-auto">
            Explore our curated selection of stunning artworks from talented artists around the world.
            Find the perfect piece to transform your space.
          </p>
          
          {/* Large Search Bar */}
          <div className="max-w-2xl mx-auto mb-56">
            <SearchBar onSearch={handleSearch} />
          </div>
          
          {/* Modern Stats Section */}
          <div className="flex justify-center items-center space-x-40 mb-16">
            <div className="text-center">
              <div className="text-2xl font-semibold text-gray-800 mb-2">60+</div>
              <div className="text-sm text-gray-600">Curated Artworks </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-semibold text-gray-800 mb-2">30+</div>
              <div className="text-sm text-gray-600"> Countries Represented</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-semibold text-gray-800 mb-2">100%</div>
              <div className="text-sm text-gray-600"> Authenticity Guaranteed</div>
            </div>
          </div>
        </div>
      </section>

      {/* Gallery Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 mb-32">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-black mb-6">Our Art Collection</h2>
            <p className="text-xl text-gray-700 max-w-3xl mx-auto">
              {searchQuery ? `Search results for "${searchQuery}"` : 'Browse our carefully curated selection of extraordinary artworks'}
            </p>
          </div>
          
          <div className="grid grid-cols-3 gap-6 max-w-6xl mx-auto">
            {displayedArt.map((art) => (
              <div key={art.id} className="bg-white rounded-xl overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300">
                <div className="relative">
                  <img
                    src={`/src/assets/images/${art.image}`}
                    alt={art.name}
                    className="w-full h-56 object-cover"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = `https://picsum.photos/400/400?random=${art.id}`;
                    }}
                  />
                </div>
                <div className="p-6 flex flex-col h-48">
                  <h3 className="text-gray-900 font-semibold text-xl h-8 overflow-hidden">{art.name}</h3>
                  <p className="text-gray-600 text-sm h-12 overflow-hidden line-clamp-2 mb-2">{art.description}</p>
                  <div className="flex justify-between items-center h-8">
                    <span className="text-gray-900 font-bold text-lg">${art.price.toLocaleString()}</span>
                    <span className="text-gray-500 text-sm">{art.origin}</span>
                  </div>
                  <div className="mt-auto">
                    <button className="w-full bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200">
                      Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {hasMore && !loading && (
            <div className="text-center mt-16">
              <button
                onClick={loadMore}
                className="bg-gray-900 hover:bg-gray-800 text-white px-8 py-3 rounded-lg font-medium text-lg transition-colors duration-200"
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