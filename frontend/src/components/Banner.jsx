import React, { useState, useEffect } from 'react';
import './Banner.css';

const Banner = () => {
  const [isVisible, setIsVisible] = useState(true);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsAnimating(true);
      setTimeout(() => setIsVisible(false), 500);
    }, 8000);

    return () => clearTimeout(timer);
  }, []);

  const handleClose = () => {
    setIsAnimating(true);
    setTimeout(() => setIsVisible(false), 300);
  };

  if (!isVisible) return null;

  return (
    <div className={`banner ${isAnimating ? 'banner-fade-out' : ''}`}>
      <div className="banner-inner">
        <div className="banner-content">
          <p className="banner-description">
          Shop art by feeling. Artisty’s closed-loop AI agent searches, navigates, and manages your cart in real time.
          </p>
          <div className="banner-tech">
            <span className="tech-label">Tech Stack</span>
            <div className="tech-stack">
              <span className="tech-item">React</span>
              <span className="tech-item">JS</span>
              <span className="tech-item">Python</span>
              <span className="tech-item">LangChain</span>
              <span className="tech-item">OpenAI</span>
              <span className="tech-item">AWS Amplify</span>
              <span className="tech-item">AWS API Gateway</span>
              <span className="tech-item">AWS Lambda</span>
              <span className="tech-item">AWS S3</span>
              <span className="tech-item">AWS CloudWatch</span>
            </div>
            <div className="banner-developer">Developed by KAI</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Banner;
