import React, { useState, useEffect } from 'react';
import './CartPage.css';

const CartPage = ({ cart, onRemoveFromCart, onGoBack }) => {
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  
  useEffect(() => {
    if (showCheckoutModal) {
      const timer = setTimeout(() => {
        setShowCheckoutModal(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [showCheckoutModal]);
  
  useEffect(() => {
    const handleTriggerCheckout = () => {
      console.log('[DEBUG] CartPage received triggerCheckout event');
      setShowCheckoutModal(true);
    };
    
    window.addEventListener('triggerCheckout', handleTriggerCheckout);
    return () => window.removeEventListener('triggerCheckout', handleTriggerCheckout);
  }, []);
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + item.price, 0);
  };

  const getItemCount = (itemId) => {
    return cart.filter(item => item.id === itemId).length;
  };

  const getUniqueItems = () => {
    const uniqueMap = new Map();
    cart.forEach(item => {
      if (uniqueMap.has(item.id)) {
        uniqueMap.get(item.id).quantity += 1;
      } else {
        uniqueMap.set(item.id, { ...item, quantity: 1 });
      }
    });
    return Array.from(uniqueMap.values());
  };

  if (cart.length === 0) {
    return (
      <div className="cart-page">
        <div className="cart-container">
          <div className="cart-header">
            <button onClick={onGoBack} className="cart-back-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Gallery
            </button>
            <h1 className="cart-title">Your Cart</h1>
          </div>
          
          <div className="cart-empty">
            <div className="cart-empty-icon">🛍️</div>
            <h2>Your cart is empty</h2>
            <p>Discover our beautiful artworks and add them to your cart</p>
            <button onClick={onGoBack} className="cart-continue-shopping">
              Continue Shopping
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <div className="cart-container">
        <div className="cart-header">
          <button onClick={onGoBack} className="cart-back-btn">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="20" height="20">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Gallery
          </button>
          <h1 className="cart-title">Your Cart ({cart.length} items)</h1>
        </div>

        <div className="cart-content">
          <div className="cart-items">
            {getUniqueItems().map((item) => (
              <div key={item.id} className="cart-item">
                <div className="cart-item-image">
                  <img
                    src={new URL(`../assets/images/${item.image}`, import.meta.url).href}
                    alt={item.name}
                  />
                </div>
                
                <div className="cart-item-details">
                  <h3 className="cart-item-name">{item.name}</h3>
                  <p className="cart-item-origin">{item.origin}</p>
                  <p className="cart-item-description">{item.description}</p>
                </div>
                
                <div className="cart-item-actions">
                  <div className="cart-item-quantity">
                    <span>Qty: {item.quantity}</span>
                  </div>
                  <div className="cart-item-price">
                    {formatPrice(item.price)}
                  </div>
                  <button 
                    onClick={() => onRemoveFromCart(item.id)}
                    className="cart-item-remove"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="cart-summary">
            <div className="cart-summary-content">
              <h3>Order Summary</h3>
              <div className="cart-summary-line">
                <span>Subtotal ({cart.length} items)</span>
                <span>{formatPrice(getTotalPrice())}</span>
              </div>
              <div className="cart-summary-line">
                <span>Shipping</span>
                <span>{getTotalPrice() > 1500 ? 'Free' : '$150'}</span>
              </div>
              <div className="cart-summary-line cart-total">
                <span>Total</span>
                <span>{formatPrice(getTotalPrice() + (getTotalPrice() > 1500 ? 0 : 150))}</span>
              </div>
              
              <button 
                className="cart-checkout-btn"
                onClick={() => setShowCheckoutModal(true)}
              >
                Proceed to Checkout
              </button>
              
              <button onClick={onGoBack} className="cart-continue-shopping">
                Continue Shopping
              </button>
            </div>
          </div>
        </div>
        
        {/* Checkout Modal */}
        {showCheckoutModal && (
          <div className="checkout-modal-overlay">
            <div className="checkout-modal-content">
              <div className="checkout-spinner"></div>
              <h3>Redirecting to Payment...</h3>
              <p>Payment system is currently in development</p>
              <button 
                onClick={() => setShowCheckoutModal(false)}
                className="checkout-close-btn"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartPage;