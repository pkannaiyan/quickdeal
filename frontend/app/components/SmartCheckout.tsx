'use client';

import { useState, useEffect } from 'react';
import JioMartCheckout from './JioMartCheckout';

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

interface SmartCheckoutProps {
  product: Product;
  onClose: () => void;
  userLocation?: { city: string; pincode: string };
}

// Platform configurations with direct product/cart URLs
const PLATFORM_CONFIG: Record<string, {
  name: string;
  logo: string;
  color: string;
  // Different URL strategies
  searchUrl: (q: string) => string;
  appDeepLink: (q: string) => string;
  playStore: string;
  appStore: string;
  instructions: string[];
}> = {
  blinkit: {
    name: 'Blinkit',
    logo: '🟢',
    color: '#0c831f',
    searchUrl: (q) => `https://blinkit.com/s/?q=${encodeURIComponent(q)}`,
    appDeepLink: (q) => `blinkit://search?q=${encodeURIComponent(q)}`,
    playStore: 'https://play.google.com/store/apps/details?id=com.grofers.customerapp',
    appStore: 'https://apps.apple.com/app/blinkit/id1493235233',
    instructions: [
      '1. App will open to the product',
      '2. Tap "Add to Cart"', 
      '3. Tap cart icon → Checkout',
      '4. Select payment → Done!'
    ]
  },
  zepto: {
    name: 'Zepto',
    logo: '🟣', 
    color: '#8b5cf6',
    searchUrl: (q) => `https://www.zeptonow.com/search?query=${encodeURIComponent(q)}`,
    appDeepLink: (q) => `zepto://search?query=${encodeURIComponent(q)}`,
    playStore: 'https://play.google.com/store/apps/details?id=com.zeptoconsumerapp',
    appStore: 'https://apps.apple.com/app/zepto/id1575323645',
    instructions: [
      '1. App will search the product',
      '2. Tap product → "Add"',
      '3. Tap cart → "Checkout"',
      '4. Pay & get in 10 mins!'
    ]
  },
  instamart: {
    name: 'Swiggy Instamart',
    logo: '🟠',
    color: '#fc8019',
    searchUrl: (q) => `https://www.swiggy.com/instamart/search?query=${encodeURIComponent(q)}`,
    appDeepLink: (q) => `swiggy://instamart/search?query=${encodeURIComponent(q)}`,
    playStore: 'https://play.google.com/store/apps/details?id=in.swiggy.android',
    appStore: 'https://apps.apple.com/app/swiggy/id989540920',
    instructions: [
      '1. Swiggy app opens to Instamart',
      '2. Tap product → "Add"',
      '3. View cart → "Checkout"',
      '4. Complete payment!'
    ]
  },
  bigbasket: {
    name: 'BigBasket',
    logo: '🟢',
    color: '#84c225',
    searchUrl: (q) => `https://www.bigbasket.com/ps/?q=${encodeURIComponent(q)}`,
    appDeepLink: (q) => `bigbasket://search?q=${encodeURIComponent(q)}`,
    playStore: 'https://play.google.com/store/apps/details?id=com.bigbasket.mobileapp',
    appStore: 'https://apps.apple.com/app/bigbasket/id660683603',
    instructions: [
      '1. App opens to search results',
      '2. Tap "Add" on the product',
      '3. Go to cart → Checkout',
      '4. Choose slot & pay!'
    ]
  },
  jiomart: {
    name: 'JioMart',
    logo: '🔵',
    color: '#0078ad',
    searchUrl: (q) => `https://www.jiomart.com/search?q=${encodeURIComponent(q)}`,
    appDeepLink: (q) => `jiomart://search?q=${encodeURIComponent(q)}`,
    playStore: 'https://play.google.com/store/apps/details?id=com.jio.jiomart',
    appStore: 'https://apps.apple.com/app/jiomart/id1498798498',
    instructions: [
      '1. JioMart app opens',
      '2. Tap product → "Add to Basket"',
      '3. View basket → Checkout',
      '4. Pay with any method!'
    ]
  },
};

export default function SmartCheckout({ product, onClose, userLocation }: SmartCheckoutProps) {
  const [step, setStep] = useState<'select' | 'ready' | 'opening'>('select');
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  const [openMethod, setOpenMethod] = useState<'app' | 'web'>('app');
  const [quantity, setQuantity] = useState(1);
  const [copied, setCopied] = useState(false);
  
  // JioMart direct checkout
  const [showJioMartCheckout, setShowJioMartCheckout] = useState(false);
  const [jioMartEnabled, setJioMartEnabled] = useState(false);
  
  // Check if JioMart integration is enabled
  useEffect(() => {
    checkJioMartStatus();
  }, []);
  
  const checkJioMartStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/jiomart/status`);
      const data = await response.json();
      setJioMartEnabled(data.configured || data.logged_in);
    } catch {
      // JioMart integration not available
    }
  };

  // Auto-select best platform
  useEffect(() => {
    const best = product.prices
      .filter(p => p.is_available)
      .sort((a, b) => a.price - b.price)[0];
    if (best) {
      setSelectedPlatform(best.platform);
    }
  }, [product.prices]);

  const selectedPrice = product.prices.find(p => p.platform === selectedPlatform);
  const config = selectedPlatform ? PLATFORM_CONFIG[selectedPlatform] : null;

  // Copy product name for easy pasting
  const copyProductName = () => {
    navigator.clipboard.writeText(product.product_name);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Track order
  const trackOrder = async () => {
    try {
      await fetch(`${API_URL}/api/analytics/track/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: product.product_id,
          product_name: product.product_name,
          selected_platform: selectedPlatform,
          price: selectedPrice?.price || product.lowest_price,
          quantity,
          location: userLocation,
          checkout_method: openMethod
        })
      });
    } catch (e) {
      console.error('Track error:', e);
    }
  };

  // Open platform
  const openPlatform = async () => {
    if (!selectedPlatform || !config) return;

    setStep('opening');
    await trackOrder();

    const productName = product.product_name;

    if (openMethod === 'app') {
      // Try to open app first
      const appUrl = config.appDeepLink(productName);
      const webUrl = config.searchUrl(productName);

      // Create hidden iframe to try app deep link
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      iframe.src = appUrl;
      document.body.appendChild(iframe);

      // Fallback to web after delay if app doesn't open
      setTimeout(() => {
        document.body.removeChild(iframe);
        // Open web as fallback
        window.open(webUrl, '_blank');
      }, 1500);
    } else {
      // Direct web open
      window.open(config.searchUrl(productName), '_blank');
    }

    // Show success after a moment
    setTimeout(() => {
      setStep('select');
    }, 3000);
  };

  const totalAmount = (selectedPrice?.price || product.lowest_price) * quantity;

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
        <div className="sticky top-0 z-10 bg-gradient-to-r from-emerald-500/20 to-green-600/20 p-6 border-b border-white/10 backdrop-blur-xl">
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center text-2xl animate-pulse">
                ⚡
              </div>
              <div>
                <h2 className="font-display text-xl font-bold">Smart Checkout</h2>
                <p className="text-gray-400 text-sm">Fastest way to order</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg">
              ✕
            </button>
          </div>
        </div>

        {/* Product Info */}
        <div className="p-4 bg-white/5 border-b border-white/10">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-white/10 rounded-xl flex items-center justify-center text-3xl flex-shrink-0">
              🛍️
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold line-clamp-2">{product.product_name}</h3>
              <div className="flex items-center gap-2 mt-1 text-sm text-gray-400">
                {product.brand && <span>{product.brand}</span>}
                <span>•</span>
                <span>{product.quantity}</span>
              </div>
              <button
                onClick={copyProductName}
                className="mt-2 text-xs bg-white/10 hover:bg-white/20 px-2 py-1 rounded-lg flex items-center gap-1"
              >
                {copied ? '✓ Copied!' : '📋 Copy product name'}
              </button>
            </div>
            <div className="text-right flex-shrink-0">
              <div className="text-xl font-bold text-green-400">₹{totalAmount}</div>
              <div className="flex items-center gap-2 mt-1">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="w-6 h-6 rounded bg-white/10 hover:bg-white/20 text-sm"
                >-</button>
                <span className="w-6 text-center text-sm">{quantity}</span>
                <button
                  onClick={() => setQuantity(Math.min(10, quantity + 1))}
                  className="w-6 h-6 rounded bg-white/10 hover:bg-white/20 text-sm"
                >+</button>
              </div>
            </div>
          </div>
        </div>

        {/* Important Notice */}
        <div className="p-4 bg-amber-500/10 border-b border-amber-500/20">
          <div className="flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <div className="text-sm">
              <p className="font-semibold text-amber-400">Why can&apos;t we add directly to cart?</p>
              <p className="text-gray-400 mt-1">
                Blinkit, Zepto, JioMart etc. don&apos;t allow third-party cart access. 
                We&apos;ll open the app/site directly to the product for fastest checkout.
              </p>
            </div>
          </div>
        </div>

        {/* Platform Selection */}
        {step === 'select' && (
          <div className="p-4">
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              🛒 Select Platform
              <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                Best price highlighted
              </span>
            </h4>

            <div className="space-y-2">
              {product.prices
                .filter(p => p.is_available)
                .sort((a, b) => a.price - b.price)
                .map((price, index) => {
                  const cfg = PLATFORM_CONFIG[price.platform];
                  const isSelected = selectedPlatform === price.platform;
                  const isBest = index === 0;

                  return (
                    <button
                      key={price.platform}
                      onClick={() => setSelectedPlatform(price.platform)}
                      className={`w-full p-3 rounded-xl transition-all flex items-center justify-between ${
                        isSelected
                          ? 'bg-green-500/20 border-2 border-green-500'
                          : isBest
                          ? 'bg-yellow-500/10 border border-yellow-500/30 hover:bg-yellow-500/20'
                          : 'bg-white/5 border border-white/10 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{cfg?.logo || '🛒'}</span>
                        <div className="text-left">
                          <div className="font-medium flex items-center gap-2">
                            {cfg?.name || price.platform_name}
                            {isBest && (
                              <span className="text-[10px] bg-yellow-500/30 text-yellow-400 px-1.5 py-0.5 rounded">
                                BEST
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-gray-400">{price.delivery_time}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`font-bold ${isBest ? 'text-yellow-400' : ''}`}>
                          ₹{price.price * quantity}
                        </div>
                        {price.discount_percent > 0 && (
                          <div className="text-[10px] text-green-400">{price.discount_percent.toFixed(0)}% off</div>
                        )}
                      </div>
                    </button>
                  );
                })}
            </div>

            {/* JioMart Direct Checkout (if selected and enabled) */}
            {selectedPlatform === 'jiomart' && jioMartEnabled && (
              <div className="mt-4 p-4 bg-gradient-to-r from-blue-600/20 to-blue-700/20 border border-blue-500/30 rounded-xl">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold">
                    J
                  </div>
                  <div>
                    <div className="font-bold text-blue-400">🔥 Direct Checkout Available!</div>
                    <div className="text-xs text-gray-400">Order directly without leaving the app</div>
                  </div>
                </div>
                <button
                  onClick={() => setShowJioMartCheckout(true)}
                  className="w-full py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 rounded-lg font-bold flex items-center justify-center gap-2"
                >
                  ⚡ One-Click JioMart Order
                </button>
              </div>
            )}

            {/* Open Method */}
            <div className="mt-4">
              <h5 className="text-sm text-gray-400 mb-2">
                {selectedPlatform === 'jiomart' && jioMartEnabled 
                  ? 'Or open manually:' 
                  : 'Open with:'}
              </h5>
              <div className="flex gap-2">
                <button
                  onClick={() => setOpenMethod('app')}
                  className={`flex-1 p-3 rounded-xl border transition-all ${
                    openMethod === 'app'
                      ? 'bg-green-500/20 border-green-500'
                      : 'bg-white/5 border-white/10 hover:bg-white/10'
                  }`}
                >
                  <div className="text-xl mb-1">📱</div>
                  <div className="text-sm font-medium">App</div>
                  <div className="text-[10px] text-gray-400">Faster checkout</div>
                </button>
                <button
                  onClick={() => setOpenMethod('web')}
                  className={`flex-1 p-3 rounded-xl border transition-all ${
                    openMethod === 'web'
                      ? 'bg-green-500/20 border-green-500'
                      : 'bg-white/5 border-white/10 hover:bg-white/10'
                  }`}
                >
                  <div className="text-xl mb-1">🌐</div>
                  <div className="text-sm font-medium">Website</div>
                  <div className="text-[10px] text-gray-400">No app needed</div>
                </button>
              </div>
            </div>

            {/* Instructions Preview */}
            {config && (
              <div className="mt-4 p-4 bg-white/5 rounded-xl">
                <h5 className="font-medium mb-2 flex items-center gap-2">
                  <span className="text-lg">{config.logo}</span>
                  Quick Steps for {config.name}:
                </h5>
                <ol className="text-sm text-gray-400 space-y-1">
                  {config.instructions.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>
            )}

            {/* Action Button */}
            <button
              onClick={() => setStep('ready')}
              disabled={!selectedPlatform}
              className="w-full mt-4 py-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-600 disabled:to-gray-700 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-2"
            >
              ⚡ Continue to Checkout
            </button>
          </div>
        )}

        {/* Ready to Open */}
        {step === 'ready' && config && (
          <div className="p-6">
            <div className="text-center mb-6">
              <div className="w-20 h-20 mx-auto mb-4 rounded-2xl flex items-center justify-center text-5xl"
                   style={{ backgroundColor: `${config.color}20` }}>
                {config.logo}
              </div>
              <h3 className="text-xl font-bold">{config.name}</h3>
              <p className="text-gray-400 mt-1">Ready to open</p>
            </div>

            {/* Order Summary */}
            <div className="bg-white/5 rounded-xl p-4 mb-4">
              <div className="flex justify-between mb-2">
                <span className="text-gray-400">Product</span>
                <span className="text-right max-w-[180px] truncate">{product.product_name}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-400">Quantity</span>
                <span>{quantity}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-gray-400">Platform</span>
                <span>{config.name}</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-white/10 font-bold">
                <span>Est. Total</span>
                <span className="text-green-400">₹{totalAmount}</span>
              </div>
            </div>

            {/* Steps reminder */}
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 mb-4">
              <p className="font-medium text-blue-400 mb-2">📋 After opening:</p>
              <ol className="text-sm text-gray-300 space-y-1">
                {config.instructions.map((instruction, i) => (
                  <li key={i}>{instruction}</li>
                ))}
              </ol>
            </div>

            {/* Buttons */}
            <div className="space-y-3">
              <button
                onClick={openPlatform}
                className="w-full py-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 rounded-xl font-bold text-lg transition-all flex items-center justify-center gap-2"
              >
                {openMethod === 'app' ? '📱' : '🌐'} Open {config.name}
              </button>
              <button
                onClick={() => setStep('select')}
                className="w-full py-3 bg-white/10 hover:bg-white/20 rounded-xl font-medium"
              >
                ← Back to platforms
              </button>
            </div>

            {/* App store links */}
            <div className="mt-4 pt-4 border-t border-white/10">
              <p className="text-xs text-gray-500 text-center mb-2">Don&apos;t have the app?</p>
              <div className="flex justify-center gap-4">
                <a
                  href={config.playStore}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-gray-400 hover:text-white flex items-center gap-1"
                >
                  <span>▶️</span> Play Store
                </a>
                <a
                  href={config.appStore}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-gray-400 hover:text-white flex items-center gap-1"
                >
                  <span>🍎</span> App Store
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Opening Animation */}
        {step === 'opening' && config && (
          <div className="p-12 text-center">
            <div className="w-24 h-24 mx-auto mb-6 relative">
              <div className="absolute inset-0 bg-green-500/20 rounded-full animate-ping" />
              <div className="relative w-full h-full rounded-2xl flex items-center justify-center text-5xl"
                   style={{ backgroundColor: `${config.color}30` }}>
                {config.logo}
              </div>
            </div>
            <h3 className="text-xl font-bold mb-2">Opening {config.name}...</h3>
            <p className="text-gray-400 mb-4">
              {openMethod === 'app' ? 'Launching app...' : 'Opening website...'}
            </p>
            <div className="flex justify-center gap-1">
              {[0, 1, 2, 3, 4].map(i => (
                <div
                  key={i}
                  className="w-2 h-8 bg-green-500 rounded animate-pulse"
                  style={{ animationDelay: `${i * 100}ms` }}
                />
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* JioMart Direct Checkout Modal */}
      {showJioMartCheckout && (
        <JioMartCheckout
          product={product}
          onClose={() => setShowJioMartCheckout(false)}
          onSuccess={(orderId) => {
            console.log('JioMart order placed:', orderId);
            setShowJioMartCheckout(false);
            onClose();
          }}
        />
      )}
    </div>
  );
}

