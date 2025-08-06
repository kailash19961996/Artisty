import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white py-12">
      <div className="container mx-auto px-4">
        {/* Main Content */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-6 h-6 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm">🎨</span>
            </div>
            <span className="text-xl font-medium text-black">Artisty</span>
          </div>
          <p className="text-gray-600 max-w-md mx-auto">
            Discover extraordinary art pieces from talented artists around the world. Our curated collection brings beauty and inspiration to your space.
          </p>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-200 pt-8 flex flex-col sm:flex-row justify-between items-center text-sm text-gray-500">
          <p>© 2024 Artisty. All rights reserved.</p>
          <div className="flex space-x-6 mt-4 sm:mt-0">
            <a href="#terms" className="hover:text-gray-700 transition-colors">Terms</a>
            <a href="#privacy" className="hover:text-gray-700 transition-colors">Privacy</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;