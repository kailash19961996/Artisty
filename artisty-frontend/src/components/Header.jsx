import React from 'react';

const Header = () => {
  return (
    <header className="bg-white bg-opacity-10 backdrop-filter backdrop-blur-lg sticky top-0 z-50 px-6 py-4">
      <div className="container mx-auto">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-white text-lg">🎨</span>
            </div>
            <span className="text-xl font-medium text-black">Artisty</span>
          </div>

          {/* Navigation */}
          <div className="flex items-center space-x-8">
            {/* Regular Links */}
            <nav className="hidden md:flex items-center space-x-6">
              <a href="#about" className="text-gray-600 hover:text-gray-900 font-medium">About</a>
              <a href="#menu" className="text-gray-600 hover:text-gray-900 font-medium">Menu</a>
            </nav>

            {/* Right Side Buttons */}
            <div className="flex items-center space-x-4">
              {/* Globe Icon */}
              <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
              </button>

              {/* Start Building Button */}
              <button className="bg-gray-900 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-800 transition-colors">
                Menu
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;