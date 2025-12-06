'use client';

import { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

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

interface UserDetails {
  name: string;
  phone: string;
  address: string;
  pincode: string;
  city: string;
}

interface OneClickCheckoutProps {
  product: Product;
  onClose: () => void;
  userLocation?: { city: string; pincode: string };
}

// Platform configurations with deep links and cart URLs
const PLATFORM_CONFIG: Record<string, {
  name: string;
  logo: string;
  color: string;
  webUrl: string;
  cartUrl: (product: string) => string;
  appScheme: string;
  playStore: string;
  appStore: string;
  supportsDeepLink: boolean;
}> = {
  blinkit: {
    name: 'Blinkit',
    logo: '🟢',
    color: '#0c831f',
    webUrl: 'https://blinkit.com',
    cartUrl: (p) => `https://blinkit.com/s/?q=${encodeURIComponent(p)}`,
    appScheme: 'blinkit://search?q=',
    playStore: 'https://play.google.com/store/apps/details?id=com.grofers.customerapp',
    appStore: 'https://apps.apple.com/app/blinkit/id1493235233',
    supportsDeepLink: true,
  },
  zepto: {
    name: 'Zepto',
    logo: '🟣',
    color: '#8b5cf6',
    webUrl: 'https://www.zeptonow.com',
    cartUrl: (p) => `https://www.zeptonow.com/search?query=${encodeURIComponent(p)}`,
    appScheme: 'zepto://search?q=',
    playStore: 'https://play.google.com/store/apps/details?id=com.zeptoconsumerapp',
    appStore: 'https://apps.apple.com/app/zepto/id1575323645',
    supportsDeepLink: true,
  },
  instamart: {
    name: 'Swiggy Instamart',
    logo: '🟠',
    color: '#fc8019',
    webUrl: 'https://www.swiggy.com/instamart',
    cartUrl: (p) => `https://www.swiggy.com/instamart/search?query=${encodeURIComponent(p)}`,
    appScheme: 'swiggy://instamart/search?q=',
    playStore: 'https://play.google.com/store/apps/details?id=in.swiggy.android',
    appStore: 'https://apps.apple.com/app/swiggy/id989540920',
    supportsDeepLink: true,
  },
  bigbasket: {
    name: 'BigBasket',
    logo: '🟢',
    color: '#84c225',
    webUrl: 'https://www.bigbasket.com',
    cartUrl: (p) => `https://www.bigbasket.com/ps/?q=${encodeURIComponent(p)}`,
    appScheme: 'bigbasket://search?q=',
    playStore: 'https://play.google.com/store/apps/details?id=com.bigbasket.mobileapp',
    appStore: 'https://apps.apple.com/app/bigbasket/id660683603',
    supportsDeepLink: true,
  },
  jiomart: {
    name: 'JioMart',
    logo: '🔵',
    color: '#0078ad',
    webUrl: 'https://www.jiomart.com',
    cartUrl: (p) => `https://www.jiomart.com/search?q=${encodeURIComponent(p)}`,
    appScheme: 'jiomart://search?q=',
    playStore: 'https://play.google.com/store/apps/details?id=com.jio.jiomart',
    appStore: 'https://apps.apple.com/app/jiomart/id1498798498',
    supportsDeepLink: true,
  },
};

export default function OneClickCheckout({ product, onClose, userLocation }: OneClickCheckoutProps) {
  const [step, setStep] = useState<'details' | 'platform' | 'confirm' | 'processing' | 'success'>('details');
  const [quantity, setQuantity] = useState(1);
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  const [userDetails, setUserDetails] = useState<UserDetails>({
    name: '',
    phone: '',
    address: '',
    pincode: userLocation?.pincode || '',
    city: userLocation?.city || '',
  });
  const [savedDetails, setSavedDetails] = useState(false);
  const [orderMethod, setOrderMethod] = useState<'app' | 'web'>('web');

  // Load saved user details
  useEffect(() => {
    const saved = localStorage.getItem('checkout_details');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setUserDetails(prev => ({ ...prev, ...parsed }));
        setSavedDetails(true);
      } catch {
        // Ignore parse errors
      }
    }
  }, []);

  // Get best price platform
  const bestPricePlatform = product.prices
    .filter(p => p.is_available)
    .sort((a, b) => a.price - b.price)[0];

  // Save user details
  const saveDetails = () => {
    localStorage.setItem('checkout_details', JSON.stringify(userDetails));
    setSavedDetails(true);
  };

  // Track order for analytics
  const trackOrder = async (platform: string, price: number) => {
    try {
      await fetch(`${API_URL}/api/analytics/track/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: product.product_id,
          product_name: product.product_name,
          selected_platform: platform,
          price: price,
          quantity: quantity,
          location: { city: userDetails.city, pincode: userDetails.pincode },
          checkout_method: orderMethod,
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
  };

  // Handle checkout
  const handleCheckout = async () => {
    if (!selectedPlatform) return;

    setStep('processing');

    const config = PLATFORM_CONFIG[selectedPlatform];
    const priceEntry = product.prices.find(p => p.platform === selectedPlatform);
    
    // Track the order
    await trackOrder(selectedPlatform, priceEntry?.price || product.lowest_price);

    // Save order to history
    const orderHistory = JSON.parse(localStorage.getItem('order_history') || '[]');
    orderHistory.unshift({
      id: `order-${Date.now()}`,
      product: product.product_name,
      platform: selectedPlatform,
      platform_name: config.name,
      price: priceEntry?.price || product.lowest_price,
      quantity,
      total: (priceEntry?.price || product.lowest_price) * quantity,
      address: userDetails.address,
      timestamp: new Date().toISOString(),
      status: 'redirected'
    });
    localStorage.setItem('order_history', JSON.stringify(orderHistory.slice(0, 50)));

    // Generate checkout URL
    let checkoutUrl: string;

    if (orderMethod === 'app' && config.supportsDeepLink) {
      // Try app deep link first
      checkoutUrl = `${config.appScheme}${encodeURIComponent(product.product_name)}`;
      
      // Open app, with fallback to web
      const appWindow = window.open(checkoutUrl, '_blank');
      
      // If app didn't open, fall back to web after a short delay
      setTimeout(() => {
        if (!appWindow || appWindow.closed) {
          window.open(config.cartUrl(product.product_name), '_blank');
        }
      }, 2000);
    } else {
      // Web checkout
      checkoutUrl = config.cartUrl(product.product_name);
      window.open(checkoutUrl, '_blank');
    }

    // Show success
    setTimeout(() => {
      setStep('success');
    }, 1500);
  };

  // Auto-select best platform
  useEffect(() => {
    if (bestPricePlatform && !selectedPlatform) {
      setSelectedPlatform(bestPricePlatform.platform);
    }
  }, [bestPricePlatform, selectedPlatform]);

  const selectedPrice = product.prices.find(p => p.platform === selectedPlatform);
  const totalAmount = (selectedPrice?.price || product.lowest_price) * quantity;
  const savings = (product.highest_price - (selectedPrice?.price || product.lowest_price)) * quantity;

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
        <div className="sticky top-0 z-10 bg-gradient-to-r from-green-500/20 to-emerald-600/20 p-6 border-b border-white/10 backdrop-blur-xl">
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center text-2xl">
                ⚡
              </div>
              <div>
                <h2 className="font-display text-xl font-bold">One-Click Checkout</h2>
                <p className="text-gray-400 text-sm">Fast & Easy Ordering</p>
              </div>
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

          {/* Progress Steps */}
          <div className="flex items-center justify-between mt-4">
            {['details', 'platform', 'confirm'].map((s, i) => (
              <div key={s} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  step === s ? 'bg-green-500 text-white' :
                  ['platform', 'confirm', 'processing', 'success'].indexOf(step) > i - 1 ? 'bg-green-500/30 text-green-400' :
                  'bg-white/10 text-gray-500'
                }`}>
                  {i + 1}
                </div>
                {i < 2 && (
                  <div className={`w-16 h-0.5 mx-2 ${
                    ['platform', 'confirm', 'processing', 'success'].indexOf(step) > i ? 'bg-green-500' : 'bg-white/10'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Product Summary - Always visible */}
        <div className="p-4 bg-white/5 border-b border-white/10">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white/10 rounded-xl flex items-center justify-center text-3xl">
              🛍️
            </div>
            <div className="flex-1">
              <h3 className="font-semibold line-clamp-1">{product.product_name}</h3>
              <div className="flex items-center gap-2 mt-1 text-sm text-gray-400">
                {product.brand && <span>{product.brand}</span>}
                <span>•</span>
                <span>{product.quantity}</span>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-lg font-bold text-green-400">₹{totalAmount.toFixed(0)}</span>
                {savings > 0 && (
                  <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                    Save ₹{savings.toFixed(0)}
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20"
              >
                -
              </button>
              <span className="w-8 text-center font-bold">{quantity}</span>
              <button
                onClick={() => setQuantity(Math.min(10, quantity + 1))}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20"
              >
                +
              </button>
            </div>
          </div>
        </div>

        {/* Step 1: Delivery Details */}
        {step === 'details' && (
          <div className="p-6">
            <h4 className="font-semibold mb-4 flex items-center gap-2">
              📍 Delivery Details
              {savedDetails && (
                <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                  Saved ✓
                </span>
              )}
            </h4>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 block mb-1">Name</label>
                <input
                  type="text"
                  value={userDetails.name}
                  onChange={(e) => setUserDetails({ ...userDetails, name: e.target.value })}
                  placeholder="Your name"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-green-500/50"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 block mb-1">Phone Number</label>
                <input
                  type="tel"
                  value={userDetails.phone}
                  onChange={(e) => setUserDetails({ ...userDetails, phone: e.target.value })}
                  placeholder="10-digit mobile number"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-green-500/50"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 block mb-1">Delivery Address</label>
                <textarea
                  value={userDetails.address}
                  onChange={(e) => setUserDetails({ ...userDetails, address: e.target.value })}
                  placeholder="House/Flat No., Street, Landmark..."
                  rows={2}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-green-500/50 resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Pincode</label>
                  <input
                    type="text"
                    value={userDetails.pincode}
                    onChange={(e) => setUserDetails({ ...userDetails, pincode: e.target.value })}
                    placeholder="400001"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-green-500/50"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">City</label>
                  <input
                    type="text"
                    value={userDetails.city}
                    onChange={(e) => setUserDetails({ ...userDetails, city: e.target.value })}
                    placeholder="Mumbai"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-green-500/50"
                  />
                </div>
              </div>

              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={savedDetails}
                  onChange={(e) => {
                    if (e.target.checked) saveDetails();
                    setSavedDetails(e.target.checked);
                  }}
                  className="w-4 h-4 rounded"
                />
                <span className="text-gray-400">Save details for faster checkout</span>
              </label>
            </div>

            <button
              onClick={() => setStep('platform')}
              disabled={!userDetails.name || !userDetails.phone || !userDetails.address}
              className="w-full mt-6 py-4 bg-green-500 hover:bg-green-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-xl font-bold transition-colors"
            >
              Continue to Platform Selection →
            </button>
          </div>
        )}

        {/* Step 2: Platform Selection */}
        {step === 'platform' && (
          <div className="p-6">
            <h4 className="font-semibold mb-4">🛒 Select Platform</h4>

            <div className="space-y-3">
              {product.prices
                .filter(p => p.is_available)
                .sort((a, b) => a.price - b.price)
                .map((price, index) => {
                  const config = PLATFORM_CONFIG[price.platform];
                  const isBest = index === 0;
                  const isSelected = selectedPlatform === price.platform;

                  return (
                    <button
                      key={price.platform}
                      onClick={() => setSelectedPlatform(price.platform)}
                      className={`w-full p-4 rounded-xl transition-all flex items-center justify-between ${
                        isSelected
                          ? 'bg-green-500/20 border-2 border-green-500 ring-2 ring-green-500/20'
                          : isBest
                          ? 'bg-yellow-500/10 border border-yellow-500/30 hover:bg-yellow-500/20'
                          : 'bg-white/5 border border-white/10 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{price.platform_logo}</span>
                        <div className="text-left">
                          <div className="font-semibold flex items-center gap-2">
                            {price.platform_name}
                            {isBest && (
                              <span className="text-xs bg-yellow-500/30 text-yellow-400 px-2 py-0.5 rounded-full">
                                🏆 BEST PRICE
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-400">⏱️ {price.delivery_time}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-xl font-bold ${isBest ? 'text-yellow-400' : isSelected ? 'text-green-400' : ''}`}>
                          ₹{(price.price * quantity).toFixed(0)}
                        </div>
                        {price.discount_percent > 0 && (
                          <div className="text-xs text-green-400">{price.discount_percent.toFixed(0)}% off</div>
                        )}
                      </div>
                    </button>
                  );
                })}
            </div>

            {/* Checkout Method */}
            <div className="mt-6">
              <h5 className="text-sm text-gray-400 mb-3">Checkout via:</h5>
              <div className="flex gap-3">
                <button
                  onClick={() => setOrderMethod('web')}
                  className={`flex-1 p-3 rounded-xl border transition-all ${
                    orderMethod === 'web'
                      ? 'bg-green-500/20 border-green-500'
                      : 'bg-white/5 border-white/10 hover:bg-white/10'
                  }`}
                >
                  <div className="text-xl mb-1">🌐</div>
                  <div className="text-sm font-semibold">Website</div>
                  <div className="text-xs text-gray-400">Open in browser</div>
                </button>
                <button
                  onClick={() => setOrderMethod('app')}
                  className={`flex-1 p-3 rounded-xl border transition-all ${
                    orderMethod === 'app'
                      ? 'bg-green-500/20 border-green-500'
                      : 'bg-white/5 border-white/10 hover:bg-white/10'
                  }`}
                >
                  <div className="text-xl mb-1">📱</div>
                  <div className="text-sm font-semibold">App</div>
                  <div className="text-xs text-gray-400">Faster checkout</div>
                </button>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setStep('details')}
                className="flex-1 py-3 bg-white/10 hover:bg-white/20 rounded-xl font-medium transition-colors"
              >
                ← Back
              </button>
              <button
                onClick={() => setStep('confirm')}
                className="flex-1 py-3 bg-green-500 hover:bg-green-600 rounded-xl font-bold transition-colors"
              >
                Review Order →
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Confirm */}
        {step === 'confirm' && selectedPlatform && (
          <div className="p-6">
            <h4 className="font-semibold mb-4">✅ Confirm Order</h4>

            {/* Order Summary */}
            <div className="bg-white/5 rounded-xl p-4 mb-4">
              <h5 className="text-sm text-gray-400 mb-3">Order Summary</h5>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Product</span>
                  <span className="text-right max-w-[200px] truncate">{product.product_name}</span>
                </div>
                <div className="flex justify-between">
                  <span>Quantity</span>
                  <span>{quantity}</span>
                </div>
                <div className="flex justify-between">
                  <span>Platform</span>
                  <span className="flex items-center gap-1">
                    {PLATFORM_CONFIG[selectedPlatform]?.logo} {PLATFORM_CONFIG[selectedPlatform]?.name}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Checkout via</span>
                  <span>{orderMethod === 'app' ? '📱 App' : '🌐 Website'}</span>
                </div>
                <div className="border-t border-white/10 pt-2 mt-2 flex justify-between font-bold text-lg">
                  <span>Total</span>
                  <span className="text-green-400">₹{totalAmount.toFixed(0)}</span>
                </div>
              </div>
            </div>

            {/* Delivery Address */}
            <div className="bg-white/5 rounded-xl p-4 mb-4">
              <h5 className="text-sm text-gray-400 mb-2">📍 Deliver to</h5>
              <p className="font-semibold">{userDetails.name}</p>
              <p className="text-sm text-gray-400">{userDetails.address}</p>
              <p className="text-sm text-gray-400">{userDetails.city} - {userDetails.pincode}</p>
              <p className="text-sm text-gray-400">📞 {userDetails.phone}</p>
            </div>

            {/* Info */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-6">
              <p className="text-sm text-blue-400">
                ℹ️ You&apos;ll be redirected to {PLATFORM_CONFIG[selectedPlatform]?.name} to complete payment. 
                Your delivery details will be pre-filled where possible.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep('platform')}
                className="flex-1 py-3 bg-white/10 hover:bg-white/20 rounded-xl font-medium transition-colors"
              >
                ← Back
              </button>
              <button
                onClick={handleCheckout}
                className="flex-1 py-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 rounded-xl font-bold transition-all text-lg flex items-center justify-center gap-2"
              >
                ⚡ Place Order
              </button>
            </div>
          </div>
        )}

        {/* Processing */}
        {step === 'processing' && (
          <div className="p-12 text-center">
            <div className="w-20 h-20 mx-auto mb-6 relative">
              <div className="absolute inset-0 bg-green-500/20 rounded-full animate-ping" />
              <div className="relative w-full h-full bg-green-500/30 rounded-full flex items-center justify-center text-4xl">
                🚀
              </div>
            </div>
            <h3 className="text-xl font-bold mb-2">Processing...</h3>
            <p className="text-gray-400">
              Opening {PLATFORM_CONFIG[selectedPlatform || '']?.name}...
            </p>
          </div>
        )}

        {/* Success */}
        {step === 'success' && (
          <div className="p-12 text-center">
            <div className="w-20 h-20 mx-auto mb-6 bg-green-500/20 rounded-full flex items-center justify-center text-4xl animate-bounce">
              ✅
            </div>
            <h3 className="text-xl font-bold mb-2 text-green-400">Redirected!</h3>
            <p className="text-gray-400 mb-6">
              Complete your order on {PLATFORM_CONFIG[selectedPlatform || '']?.name}
            </p>
            
            <div className="bg-white/5 rounded-xl p-4 mb-6 text-left">
              <p className="text-sm text-gray-400 mb-2">Order Details:</p>
              <p className="font-semibold">{product.product_name}</p>
              <p className="text-sm text-gray-400">
                {quantity} × ₹{selectedPrice?.price || product.lowest_price} = 
                <span className="text-green-400 font-bold"> ₹{totalAmount.toFixed(0)}</span>
              </p>
            </div>

            <button
              onClick={onClose}
              className="w-full py-3 bg-white/10 hover:bg-white/20 rounded-xl font-medium transition-colors"
            >
              Done
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

