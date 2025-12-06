'use client';

import { useState } from 'react';

interface PriceEntry {
  platform: string;
  platform_name: string;
  platform_logo: string;
  price: number;
  mrp: number;
  discount_percent: number;
  is_available: boolean;
  delivery_time: string;
  url?: string;
}

interface Product {
  product_id: string;
  product_name: string;
  brand: string | null;
  quantity: string;
  lowest_price: number;
  highest_price: number;
  best_platform: string;
  best_platform_logo: string;
  prices: PriceEntry[];
}

interface QuickOrderModalProps {
  product: Product;
  onClose: () => void;
  userLocation?: { city: string; pincode: string };
}

// Platform deep link configurations
const PLATFORM_CONFIG: { [key: string]: { 
  appScheme: string; 
  webUrl: string; 
  playStore: string;
  appStore: string;
  color: string;
}} = {
  blinkit: {
    appScheme: 'blinkit://',
    webUrl: 'https://blinkit.com',
    playStore: 'https://play.google.com/store/apps/details?id=com.grofers.customerapp',
    appStore: 'https://apps.apple.com/app/blinkit/id1493235233',
    color: '#0c831f'
  },
  zepto: {
    appScheme: 'zepto://',
    webUrl: 'https://www.zeptonow.com',
    playStore: 'https://play.google.com/store/apps/details?id=com.zeptoconsumerapp',
    appStore: 'https://apps.apple.com/app/zepto/id1575323645',
    color: '#8b5cf6'
  },
  instamart: {
    appScheme: 'swiggy://',
    webUrl: 'https://www.swiggy.com/instamart',
    playStore: 'https://play.google.com/store/apps/details?id=in.swiggy.android',
    appStore: 'https://apps.apple.com/app/swiggy/id989540920',
    color: '#fc8019'
  },
  bigbasket: {
    appScheme: 'bigbasket://',
    webUrl: 'https://www.bigbasket.com',
    playStore: 'https://play.google.com/store/apps/details?id=com.bigbasket.mobileapp',
    appStore: 'https://apps.apple.com/app/bigbasket/id660683603',
    color: '#84c225'
  },
  jiomart: {
    appScheme: 'jiomart://',
    webUrl: 'https://www.jiomart.com',
    playStore: 'https://play.google.com/store/apps/details?id=com.jio.jiomart',
    appStore: 'https://apps.apple.com/app/jiomart/id1498798498',
    color: '#0078ad'
  }
};

export default function QuickOrderModal({ product, onClose, userLocation }: QuickOrderModalProps) {
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  const [orderStep, setOrderStep] = useState<'select' | 'confirm' | 'redirect'>('select');
  const [quantity, setQuantity] = useState(1);

  // Get the best price entry
  const bestPrice = product.prices.find(p => p.price === product.lowest_price && p.is_available);

  // Generate platform-specific URL
  const getPlatformUrl = (platform: string, productName: string) => {
    const searchTerm = encodeURIComponent(productName);
    const config = PLATFORM_CONFIG[platform];
    
    if (!config) return '#';

    // Platform-specific search URLs
    const urls: { [key: string]: string } = {
      blinkit: `${config.webUrl}/s/?q=${searchTerm}`,
      zepto: `${config.webUrl}/search?query=${searchTerm}`,
      instamart: `${config.webUrl}/search?custom_back=true&query=${searchTerm}`,
      bigbasket: `${config.webUrl}/ps/?q=${searchTerm}`,
      jiomart: `${config.webUrl}/search?q=${searchTerm}`,
    };

    return urls[platform] || config.webUrl;
  };

  // Handle order placement
  const handlePlaceOrder = (platform: string) => {
    setSelectedPlatform(platform);
    setOrderStep('confirm');
  };

  // Proceed to platform
  const proceedToPlatform = async () => {
    if (!selectedPlatform) return;

    setOrderStep('redirect');

    const selectedPrice = product.prices.find(p => p.platform === selectedPlatform);
    
    // Track the order intent via API
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
      await fetch(`${API_URL}/api/analytics/track/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: product.product_id,
          product_name: product.product_name,
          selected_platform: selectedPlatform,
          price: selectedPrice?.price || product.lowest_price,
          quantity: quantity,
          location: userLocation ? { city: userLocation.city, pincode: userLocation.pincode } : null,
          all_prices: product.prices.map(p => ({
            platform: p.platform,
            price: p.price,
            is_available: p.is_available
          }))
        })
      });
    } catch (error) {
      console.error('Failed to track order:', error);
    }

    // Also store locally for backup
    const orderIntent = {
      product_id: product.product_id,
      product_name: product.product_name,
      platform: selectedPlatform,
      quantity: quantity,
      price: selectedPrice?.price,
      timestamp: new Date().toISOString(),
      user_location: userLocation
    };

    const intents = JSON.parse(localStorage.getItem('order_intents') || '[]');
    intents.push(orderIntent);
    localStorage.setItem('order_intents', JSON.stringify(intents.slice(-50))); // Keep last 50

    // Open platform in new tab
    const url = getPlatformUrl(selectedPlatform, product.product_name);
    
    setTimeout(() => {
      window.open(url, '_blank');
      onClose();
    }, 1500);
  };

  // Get platform price
  const getPlatformPrice = (platform: string) => {
    return product.prices.find(p => p.platform === platform);
  };

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="glass rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-white/10">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="font-display text-xl font-bold">🛒 Quick Order</h2>
              <p className="text-gray-400 text-sm mt-1">
                Select a platform to complete your order
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Product Info */}
        <div className="p-6 bg-white/5 border-b border-white/10">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white/10 rounded-xl flex items-center justify-center text-3xl">
              🛍️
            </div>
            <div className="flex-1">
              <h3 className="font-semibold line-clamp-2">{product.product_name}</h3>
              <div className="flex items-center gap-2 mt-1 text-sm text-gray-400">
                {product.brand && <span>{product.brand}</span>}
                {product.brand && <span>•</span>}
                <span>{product.quantity}</span>
              </div>
            </div>
          </div>

          {/* Quantity Selector */}
          <div className="mt-4 flex items-center justify-between">
            <span className="text-gray-400">Quantity:</span>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center"
              >
                -
              </button>
              <span className="w-8 text-center font-bold">{quantity}</span>
              <button
                onClick={() => setQuantity(Math.min(10, quantity + 1))}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center"
              >
                +
              </button>
            </div>
          </div>
        </div>

        {/* Step: Select Platform */}
        {orderStep === 'select' && (
          <div className="p-6">
            <h4 className="text-sm font-semibold text-gray-400 mb-4">SELECT PLATFORM</h4>
            <div className="space-y-3">
              {product.prices
                .filter(p => p.is_available)
                .sort((a, b) => a.price - b.price)
                .map((price, index) => {
                  const config = PLATFORM_CONFIG[price.platform];
                  const isBest = index === 0;
                  
                  return (
                    <button
                      key={price.platform}
                      onClick={() => handlePlaceOrder(price.platform)}
                      className={`w-full p-4 rounded-xl transition-all flex items-center justify-between ${
                        isBest 
                          ? 'bg-primary/20 border-2 border-primary hover:bg-primary/30' 
                          : 'bg-white/5 border border-white/10 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{price.platform_logo}</span>
                        <div className="text-left">
                          <div className="font-semibold flex items-center gap-2">
                            {price.platform_name}
                            {isBest && (
                              <span className="text-xs bg-primary/30 text-primary px-2 py-0.5 rounded-full">
                                BEST PRICE
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-400">{price.delivery_time}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-xl font-bold ${isBest ? 'text-primary' : ''}`}>
                          ₹{(price.price * quantity).toFixed(0)}
                        </div>
                        {quantity > 1 && (
                          <div className="text-xs text-gray-500">₹{price.price} each</div>
                        )}
                        {price.discount_percent > 0 && (
                          <div className="text-xs text-green-400">{price.discount_percent.toFixed(0)}% off</div>
                        )}
                      </div>
                    </button>
                  );
                })}
            </div>

            {/* Best Deal Highlight */}
            {bestPrice && (
              <div className="mt-4 p-4 bg-gradient-to-r from-primary/20 to-accent/20 rounded-xl border border-primary/30">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-sm text-gray-400">Save up to</span>
                    <div className="text-xl font-bold text-accent">
                      ₹{((product.highest_price - product.lowest_price) * quantity).toFixed(0)}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm text-gray-400">vs highest price</span>
                    <div className="text-lg line-through text-gray-500">
                      ₹{(product.highest_price * quantity).toFixed(0)}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step: Confirm Order */}
        {orderStep === 'confirm' && selectedPlatform && (
          <div className="p-6">
            <div className="text-center mb-6">
              <div className="text-5xl mb-4">
                {getPlatformPrice(selectedPlatform)?.platform_logo}
              </div>
              <h3 className="text-xl font-bold">
                Order on {getPlatformPrice(selectedPlatform)?.platform_name}
              </h3>
              <p className="text-gray-400 mt-2">
                You'll be redirected to complete your order
              </p>
            </div>

            {/* Order Summary */}
            <div className="bg-white/5 rounded-xl p-4 mb-6">
              <h4 className="font-semibold mb-3">Order Summary</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Product</span>
                  <span className="text-right">{product.product_name.slice(0, 30)}...</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Quantity</span>
                  <span>{quantity}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Price per unit</span>
                  <span>₹{getPlatformPrice(selectedPlatform)?.price}</span>
                </div>
                <div className="border-t border-white/10 pt-2 mt-2 flex justify-between font-bold text-lg">
                  <span>Total</span>
                  <span className="text-primary">
                    ₹{((getPlatformPrice(selectedPlatform)?.price || 0) * quantity).toFixed(0)}
                  </span>
                </div>
              </div>
            </div>

            {/* Location Info */}
            {userLocation && (
              <div className="bg-white/5 rounded-xl p-4 mb-6 flex items-center gap-3">
                <span className="text-2xl">📍</span>
                <div>
                  <div className="font-semibold">{userLocation.city}</div>
                  <div className="text-sm text-gray-400">Pincode: {userLocation.pincode}</div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={proceedToPlatform}
                className="w-full py-4 bg-primary hover:bg-primary/80 rounded-xl font-bold text-lg transition-colors flex items-center justify-center gap-2"
              >
                <span>🚀</span>
                Proceed to {getPlatformPrice(selectedPlatform)?.platform_name}
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </button>
              <button
                onClick={() => setOrderStep('select')}
                className="w-full py-3 bg-white/5 hover:bg-white/10 rounded-xl font-medium transition-colors"
              >
                ← Choose Different Platform
              </button>
            </div>

            {/* Info Note */}
            <p className="text-xs text-gray-500 text-center mt-4">
              You'll complete your order directly on {getPlatformPrice(selectedPlatform)?.platform_name}.
              Payment will be processed by them.
            </p>
          </div>
        )}

        {/* Step: Redirecting */}
        {orderStep === 'redirect' && (
          <div className="p-12 text-center">
            <div className="animate-bounce text-6xl mb-6">🛒</div>
            <h3 className="text-xl font-bold mb-2">Redirecting...</h3>
            <p className="text-gray-400">
              Opening {getPlatformPrice(selectedPlatform || '')?.platform_name} to complete your order
            </p>
            <div className="mt-6">
              <div className="w-48 h-1 bg-white/10 rounded-full mx-auto overflow-hidden">
                <div className="h-full bg-primary animate-pulse" style={{ width: '100%' }} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

