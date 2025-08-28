import React, { useState, useRef, useEffect } from 'react';

const ChatBot = ({ isOpen, onToggle }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm Purple. I can help you find the perfect artwork, answer questions about our collection, or assist with your purchase. How can I help you today?",
      isBot: true,
      timestamp: new Date(),
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [backendOnline, setBackendOnline] = useState(null); // null | true | false
  const messagesEndRef = useRef(null);
  const [mobileSize, setMobileSize] = useState('peek'); // 'peek' | 'mid' | 'full'
  const [isMobile, setIsMobile] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const mq = window.matchMedia('(max-width: 767px)');
    const sync = () => setIsMobile(mq.matches);
    sync();
    mq.addEventListener ? mq.addEventListener('change', sync) : mq.addListener(sync);
    return () => {
      mq.removeEventListener ? mq.removeEventListener('change', sync) : mq.removeListener(sync);
    };
  }, []);

  // Check backend health on mount
  useEffect(() => {
    let isMounted = true;
    fetch('/api/health')
      .then(async (res) => {
        if (!isMounted) return;
        setBackendOnline(res.ok);
      })
      .catch(() => {
        if (!isMounted) return;
        setBackendOnline(false);
      });
    return () => {
      isMounted = false;
    };
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
    const currentInput = inputText;
    setInputText('');
    setIsTyping(true);

    try {
      // Call the backend API via Vite proxy
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentInput
        }),
      });

      let data = null;
      let text = '';
      try {
        data = await response.clone().json();
      } catch (e) {
        try {
          text = await response.text();
        } catch (_) {
          text = '';
        }
      }

      if (!response.ok) {
        const errorMessage = (data && (data.error || data.message)) || text || `HTTP ${response.status}`;
        console.error('Backend returned error:', response.status, errorMessage);
        setBackendOnline(false);
        throw new Error(errorMessage);
      }

      setBackendOnline(true);
      data = data || {};
      
      // Handle AI Agent response
      const botMessage = {
        id: Date.now() + 1,
        text: data.response || 'Sorry, I encountered an error. Please try again.',
        isBot: true,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      // Handle web actions from the agent
      if (data.web_actions && data.web_actions.length > 0) {
        data.web_actions.forEach(action => {
          if (action.type === 'search') {
            // Trigger search in the main app
            triggerSearch(action.value);
          } else if (action.type === 'scroll') {
            // Trigger scroll action
            triggerScrollToSection(action.value);
          }
        });
      }
      
    } catch (error) {
      console.error('Error calling backend API:', error);
      // Fallback to local response if API fails
      const fallbackResponse = generateBotResponse(currentInput);
      const botMessage = {
        id: Date.now() + 1,
        text: `I'm having trouble connecting to my AI service right now${error?.message ? ` (reason: ${error.message})` : ''}. Here's what I can tell you locally: ${fallbackResponse}`,
        isBot: true,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  // Function to trigger search in main app
  const triggerSearch = (searchTerm) => {
    // Dispatch custom event to trigger search
    window.dispatchEvent(new CustomEvent('agentSearch', { 
      detail: { searchTerm } 
    }));
  };

  // Function to trigger scroll to specific section
  const triggerScrollToSection = (sectionId) => {
    if (sectionId === 'art-collection') {
      // Add a small delay to ensure search results are processed first
      setTimeout(() => {
        // Try to find the gallery section by ID first, then by class
        const gallerySection = document.getElementById('art-collection') ||
                             document.querySelector('.gallery-section') ||
                             document.querySelector('.gallery-container') ||
                             document.querySelector('.gallery-header');
        
        if (gallerySection) {
          gallerySection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start',
            inline: 'nearest'
          });
          console.log('🎯 Scrolled to art collection section');
        } else {
          // Fallback: scroll down to show art content
          window.scrollBy({ top: 600, behavior: 'smooth' });
          console.log('📜 Fallback scroll to show art content');
        }
      }, 800); // Slight delay to let search results load and chatbot response appear
    } else {
      // Generic scroll handling
      const scrollAmount = sectionId === 'down' ? 500 : -500;
      window.scrollBy({ top: scrollAmount, behavior: 'smooth' });
    }
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

  // Render helpers to structure bot responses
  const renderBoldSegments = (text) => {
    // Simple markdown-style bold parser for **bold** segments
    const parts = text.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, idx) => (
      idx % 2 === 1 ? <strong key={idx}>{part}</strong> : <span key={idx}>{part}</span>
    ));
  };

  const renderBotMessage = (text) => {
    if (!text) return null;
    // Detect a numbered list starting with "1. " and split into items
    const listStartIndex = text.search(/\b1\.\s/);
    if (listStartIndex >= 0) {
      const intro = text.slice(0, listStartIndex).trim();
      const listText = text.slice(listStartIndex).trim();
      // Separate any trailing concluding line from the list
      // Look for common conclusion patterns that aren't part of the numbered list
      const conclusionMatch = listText.match(/(the main suggestion[^\n\r]*|main suggestion[^\n\r]*|suggestion[^\n\r]*|enjoy[^\n\r]*|have fun[^\n\r]*|if you[^\n\r]*|just let me know[^\n\r]*|feel free[^\n\r]*|don't hesitate[^\n\r]*|let me know[^\n\r]*|🌍[^\n\r]*|✨[^\n\r]*)$/i);
      const conclusion = conclusionMatch ? conclusionMatch[0].trim() : '';
      
      // More robust approach: find the last numbered item and separate everything after it
      const lastNumberMatch = listText.match(/(\d+\.\s[^]*?)(\n\n|\r\n\r\n|$)/);
      let listOnly = listText;
      let betterConclusion = '';
      
      if (lastNumberMatch) {
        const afterLastNumber = listText.slice(lastNumberMatch.index + lastNumberMatch[1].length).trim();
        if (afterLastNumber && !afterLastNumber.match(/^\d+\./)) {
          betterConclusion = afterLastNumber;
          listOnly = listText.slice(0, lastNumberMatch.index + lastNumberMatch[1].length).trim();
        }
      }
      
      // Use the better conclusion if found, otherwise fall back to pattern match
      const finalConclusion = betterConclusion || conclusion;
      const finalListOnly = betterConclusion ? listOnly : (conclusion ? listText.slice(0, listText.length - conclusion.length).trim() : listText);

      const items = finalListOnly
        .split(/\s(?=\d+\.\s)/g)
        .map((s) => s.replace(/^\d+\.\s*/, '').trim())
        .filter(Boolean);

      return (
        <>
          {intro && <p className="bot-intro">{renderBoldSegments(intro)}</p>}
          <ol className="bot-list">
            {items.map((item, idx) => (
              <li key={idx}>{renderBoldSegments(item)}</li>
            ))}
          </ol>
          {finalConclusion && <p className="bot-paragraph">{renderBoldSegments(finalConclusion)}</p>}
        </>
      );
    }

    // Fallback: preserve line breaks as paragraphs
    return (
      <>
        {text.split(/\n{2,}|\r\n{2,}/).map((para, idx) => (
          <p className="bot-paragraph" key={idx}>{renderBoldSegments(para)}</p>
        ))}
      </>
    );
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const cycleSize = () => {
    setMobileSize((s) => (s === 'peek' ? 'mid' : s === 'mid' ? 'full' : 'peek'));
  };

  const onInputFocus = () => {
    if (isMobile && mobileSize === 'peek') setMobileSize('mid');
  };
  const onInputBlur = () => {
    // keep current; optionally shrink back
  };

  return (
    <>
      {/* Chat Button - Fixed position, only show when closed */}
      {!isOpen && (
        <button
          onClick={onToggle}
          className="chatbot-button-fixed animate-attention"
        >
        <svg className="chatbot-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        </button>
      )}

      {/* Chat Window - Split screen on desktop, bottom overlay on mobile */}
      {isOpen && (
        <div className="chatbot-panel" data-size={isMobile ? mobileSize : undefined}>
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-content">
              <div className="chatbot-header-logo">
                <div className="chatbot-header-logo-icon">
                  <span>🎨</span>
                </div>
                <div>
                  <h3>Purple</h3>
                  <p>Online now</p>
                </div>
              </div>
              {/* size toggle removed on mobile per design */}
              <button onClick={onToggle} className="chatbot-close">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message-wrapper ${message.isBot ? 'bot' : 'user'}`}
              >
                <div className={`message ${message.isBot ? 'bot' : 'user'}`}>
                  {message.isBot ? renderBotMessage(message.text) : message.text}
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
                onFocus={onInputFocus}
                onBlur={onInputBlur}
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