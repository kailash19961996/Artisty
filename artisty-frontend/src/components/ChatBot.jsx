import React, { useState, useRef, useEffect } from 'react';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your art assistant. I can help you find the perfect artwork, answer questions about our collection, or assist with your purchase. How can I help you today?",
      isBot: true,
      timestamp: new Date(),
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputText,
      isBot: false,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    // Simulate bot response (in a real app, this would call your backend API)
    setTimeout(() => {
      const botResponse = generateBotResponse(inputText);
      const botMessage = {
        id: Date.now() + 1,
        text: botResponse,
        isBot: true,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1500);
  };

  const generateBotResponse = (userInput) => {
    const input = userInput.toLowerCase();
    
    if (input.includes('price') || input.includes('cost')) {
      return "Our artworks range from $1,200 to $3,700. You can filter by price range in our gallery. Would you like me to help you find pieces within a specific budget?";
    } else if (input.includes('shipping') || input.includes('delivery')) {
      return "We offer free shipping worldwide for orders over $1,500. Standard shipping takes 5-7 business days, and we provide tracking information. Premium framing and white-glove delivery are also available.";
    } else if (input.includes('origin') || input.includes('country') || input.includes('artist')) {
      return "Our collection features artworks from over 30 countries including Italy, Japan, USA, France, and many more. Each piece includes information about its origin and artistic style. Would you like to explore works from a specific region?";
    } else if (input.includes('style') || input.includes('abstract') || input.includes('landscape')) {
      return "We have a diverse collection including abstract pieces, landscapes, contemporary art, and traditional styles. Our search feature lets you filter by style and theme. What type of artwork speaks to you?";
    } else if (input.includes('return') || input.includes('exchange')) {
      return "We offer a 30-day return policy for all artworks. Items must be returned in original condition. We also provide authenticity certificates with each purchase for your peace of mind.";
    } else if (input.includes('help') || input.includes('support')) {
      return "I'm here to help! I can assist with finding artworks, explaining our services, processing orders, or answering any questions about our collection. You can also contact our human support team at support@artisty.com.";
    } else {
      return "That's an interesting question! I can help you explore our curated collection of artworks, provide information about pricing and shipping, or assist with finding the perfect piece for your space. What specifically would you like to know about?";
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white shadow-lg hover:shadow-xl transition-all duration-300 z-50 flex items-center justify-center transform hover:scale-110 ${isOpen ? 'rotate-45' : ''}`}
      >
        {isOpen ? (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-96 bg-gradient-card rounded-xl shadow-2xl border border-white border-opacity-20 flex flex-col z-50 backdrop-filter backdrop-blur-lg">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-500 to-blue-500 text-white p-4 rounded-t-xl">
            <h3 className="font-semibold">🎨 Art Assistant</h3>
            <p className="text-sm text-white text-opacity-90">Online now</p>
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                    message.isBot
                      ? 'bg-gradient-box text-gray-800 border border-white border-opacity-30'
                      : 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                  }`}
                >
                  {message.text}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex justify-start">
                <div className="max-w-xs px-4 py-2 rounded-lg text-sm bg-gradient-box text-gray-800 border border-white border-opacity-30">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-white border-opacity-20">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about our artworks..."
                className="flex-1 border border-white border-opacity-30 rounded-lg px-3 py-2 text-sm bg-white bg-opacity-50 backdrop-filter backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 placeholder-gray-600"
              />
              <button
                onClick={handleSend}
                disabled={!inputText.trim()}
                className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 disabled:from-gray-300 disabled:to-gray-300 text-white px-4 py-2 rounded-lg text-sm transition-all duration-200 transform hover:scale-105"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatBot;