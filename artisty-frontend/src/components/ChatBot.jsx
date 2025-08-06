import React, { useState, useRef, useEffect } from 'react';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
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
  const chatBotRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle dragging
  const handleMouseDown = (e) => {
    if (!isOpen) { // Only allow dragging when closed
      setIsDragging(true);
      const rect = chatBotRef.current.getBoundingClientRect();
      setDragOffset({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging && !isOpen) {
      const newX = e.clientX - dragOffset.x;
      const newY = e.clientY - dragOffset.y;
      
      // Keep within screen bounds
      const maxX = window.innerWidth - 64; // 64px is button width
      const maxY = window.innerHeight - 64; // 64px is button height
      
      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY)),
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, dragOffset]);

  // Initialize position and handle window resize
  useEffect(() => {
    const initializePosition = () => {
      setPosition({
        x: window.innerWidth - 100,
        y: window.innerHeight - 100
      });
    };

    const handleResize = () => {
      setPosition(prev => ({
        x: Math.min(prev.x, window.innerWidth - 64),
        y: Math.min(prev.y, window.innerHeight - 64)
      }));
    };

    // Initialize position on first load
    initializePosition();

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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
        ref={chatBotRef}
        onClick={() => setIsOpen(!isOpen)}
        onMouseDown={handleMouseDown}
        className={`chatbot-button ${isOpen ? 'open' : ''} ${!isOpen ? 'animate-shake' : ''}`}
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
          cursor: isDragging ? 'grabbing' : (!isOpen ? 'grab' : 'pointer')
        }}
      >
        {isOpen ? (
          <svg className="chatbot-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="chatbot-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div 
          className="chatbot-window"
          style={{
            left: `${Math.min(position.x, Math.max(20, window.innerWidth - 420))}px`, // 420px is window width + margin
            top: `${Math.max(Math.min(position.y - 520, window.innerHeight - 540), 20)}px`, // 520px is window height + margin
          }}
        >
          {/* Header */}
          <div className="chatbot-header">
            <h3>🎨 Art Assistant</h3>
            <p>Online now</p>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message-wrapper ${message.isBot ? 'bot' : 'user'}`}
              >
                <div className={`message ${message.isBot ? 'bot' : 'user'}`}>
                  {message.text}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message-wrapper bot">
                <div className="message bot">
                  <div className="typing-indicator">
                    <div className="typing-dot purple"></div>
                    <div className="typing-dot blue"></div>
                    <div className="typing-dot purple"></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="chatbot-input-area">
            <div className="chatbot-input-wrapper">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about our artworks..."
                className="chatbot-input"
              />
              <button
                onClick={handleSend}
                disabled={!inputText.trim()}
                className="chatbot-send-btn"
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