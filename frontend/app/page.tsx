'use client';

import { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import PlatformBadges from './components/PlatformBadges';
import ComparisonCard from './components/ComparisonCard';
import DealsSection from './components/DealsSection';
import StatsBar from './components/StatsBar';
import AuthModal from './components/AuthModal';
import UserMenu from './components/UserMenu';
import LocationPicker from './components/LocationPicker';
import QuickOrderModal from './components/QuickOrderModal';
import OneClickCheckout from './components/OneClickCheckout';
import SmartCheckout from './components/SmartCheckout';
import Chatbot from './components/Chatbot';
import NegotiateModal from './components/NegotiateModal';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

interface Location {
  city: string;
  pincode: string;
  state: string;
  lat: number;
  lng: number;
}

interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  default_pincode: string;
  default_city: string;
}

interface PriceEntry {
  platform: string;
  platform_name: string;
  platform_logo: string;
  price: number;
  mrp: number;
  discount_percent: number;
  is_available: boolean;
  delivery_time: string;
  url: string;
}

interface SearchResult {
  product_id: string;
  product_name: string;
  brand: string | null;
  category: string;
  quantity: string;
  image_url: string | null;
  lowest_price: number;
  highest_price: number;
  savings_percent: number;
  best_platform: string;
  best_platform_logo: string;
  best_delivery_time: string;
  available_on: number;
  prices: PriceEntry[];
}

interface SearchResponse {
  query: string;
  total_results: number;
  platforms_searched: string[];
  results: SearchResult[];
}

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<SearchResult | null>(null);
  const [showDeals, setShowDeals] = useState(true);
  
  // Auth state
  const [user, setUser] = useState<User | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  
  // Location state
  const [currentLocation, setCurrentLocation] = useState<Location>({
    city: 'Mumbai',
    pincode: '400001',
    state: 'Maharashtra',
    lat: 19.0760,
    lng: 72.8777
  });
  const [showLocationPicker, setShowLocationPicker] = useState(false);
  
  // Quick Order state
  const [quickOrderProduct, setQuickOrderProduct] = useState<SearchResult | null>(null);
  
  // One-Click Checkout state
  const [checkoutProduct, setCheckoutProduct] = useState<SearchResult | null>(null);
  
  // Smart Checkout state (faster checkout flow)
  const [smartCheckoutProduct, setSmartCheckoutProduct] = useState<SearchResult | null>(null);
  
  // Negotiate modal state
  const [negotiateProduct, setNegotiateProduct] = useState<SearchResult | null>(null);
  
  // Check for existing session and location on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    const savedLocation = localStorage.getItem('location');
    
    if (savedLocation) {
      try {
        setCurrentLocation(JSON.parse(savedLocation));
      } catch {
        // Use default
      }
    }
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
      }
    }
  }, []);
  
  const handleLoginSuccess = (loggedInUser: User, accessToken: string) => {
    setUser(loggedInUser);
    setToken(accessToken);
    setShowAuthModal(false);
  };
  
  const handleLogout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };
  
  const handleLocationChange = (location: Location) => {
    setCurrentLocation(location);
    localStorage.setItem('location', JSON.stringify(location));
    // Refresh search results with new location
    if (searchQuery) {
      handleSearch(searchQuery);
    }
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    
    setSearchQuery(query);
    setLoading(true);
    setError(null);
    setShowDeals(false);
    
    try {
      const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}&pincode=${currentLocation.pincode}`);
      
      if (!response.ok) {
        throw new Error('Search failed');
      }
      
      const data: SearchResponse = await response.json();
      setResults(data.results);
      
      if (data.results.length === 0) {
        setError('No products found. Try a different search term.');
      }
    } catch (err) {
      setError('Failed to search. Make sure the API server is running.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setResults([]);
    setSelectedProduct(null);
    setShowDeals(true);
    setError(null);
  };

  return (
    <main className="min-h-screen">
      {/* Auth Modal */}
      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onLoginSuccess={handleLoginSuccess}
      />
      
      {/* Location Picker Modal */}
      <LocationPicker
        isOpen={showLocationPicker}
        onClose={() => setShowLocationPicker(false)}
        currentPincode={currentLocation.pincode}
        currentCity={currentLocation.city}
        onLocationChange={handleLocationChange}
      />
      
      {/* Hero Section */}
      <header className="relative overflow-hidden pt-4">
        {/* Top Navigation */}
        <div className="relative max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between py-4 border-b border-white/5">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#00D9A5] to-[#00B894] flex items-center justify-center text-2xl shadow-lg glow-mint">
                ⚡
              </div>
              <div>
                <h1 className="text-xl font-bold">
                  <span className="gradient-text">QuickDeal</span>
                </h1>
                <p className="text-xs text-gray-500">Compare • Negotiate • Save</p>
              </div>
            </div>
            
            {/* Center - Location */}
            <button 
              onClick={() => setShowLocationPicker(true)}
              className="hidden md:flex items-center gap-2 px-4 py-2.5 glass rounded-full hover:bg-white/10 transition-colors"
            >
              <span className="text-lg">📍</span>
              <span className="font-medium">{currentLocation.city}</span>
              <span className="text-gray-600">•</span>
              <span className="text-[#00D9A5] font-mono text-sm">{currentLocation.pincode}</span>
              <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            
            {/* Right - Navigation */}
            <div className="flex items-center gap-2">
              <a href="/dashboard" className="nav-item text-sm text-gray-400 hover:text-white hidden md:block">
                📊 Analytics
              </a>
              <a href="/buyer" className="nav-item text-sm text-gray-400 hover:text-white hidden md:block">
                🛒 Buyer
              </a>
              <a href="/seller" className="nav-item text-sm text-gray-400 hover:text-white hidden md:block">
                🏪 Seller
              </a>
              {user ? (
                <UserMenu user={user} onLogout={handleLogout} />
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="px-5 py-2.5 btn-primary rounded-full text-sm"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Hero Content */}
        <div className="relative max-w-7xl mx-auto px-4 py-16 md:py-24">
          {/* Background Glow */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-gradient-to-r from-purple-600/10 via-[#00D9A5]/10 to-blue-600/10 rounded-full blur-3xl" />
          </div>
          
          <div className="relative text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 glass rounded-full text-sm text-gray-400 mb-6">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00D9A5] opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00D9A5]" />
              </span>
              Live prices from 5 platforms
            </div>
            
            <h2 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              Compare. <span className="gradient-text">Negotiate.</span>
              <br />
              Get the Best Deal.
            </h2>
            
            <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto mb-4">
              Find lowest prices across{' '}
              <span className="text-yellow-400 font-medium">Blinkit</span>,{' '}
              <span className="text-purple-400 font-medium">Zepto</span>,{' '}
              <span className="text-orange-400 font-medium">Instamart</span>,{' '}
              <span className="text-lime-400 font-medium">BigBasket</span> &{' '}
              <span className="text-blue-400 font-medium">JioMart</span>
              {' '}— then negotiate for even better prices!
            </p>
            
            <p className="text-[#00D9A5] font-medium text-lg">
              🔥 Save up to 50% with smart negotiation!
            </p>
          </div>
          
          {/* Search Bar */}
          <div className="relative z-10">
            <SearchBar 
              onSearch={handleSearch} 
              loading={loading}
            />
          </div>
          
          {/* Stats */}
          <StatsBar 
            platformsCount={5}
            productsCount={1500}
            avgSavings={25}
          />
        </div>
      </header>
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 pb-12">
        {/* Search Results Header */}
        {results.length > 0 && (
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-2xl font-bold">
                Found <span className="text-[#00D9A5]">{results.length}</span> products
              </h3>
              <p className="text-gray-500 text-sm">
                Showing results for &ldquo;{searchQuery}&rdquo;
              </p>
            </div>
            <button
              onClick={handleClearSearch}
              className="px-4 py-2 glass rounded-xl hover:bg-white/10 transition-colors text-sm flex items-center gap-2"
            >
              <span>✕</span>
              Clear Search
            </button>
          </div>
        )}
        
        {/* Error Message */}
        {error && (
          <div className="glass rounded-xl p-6 text-center mb-8 border-red-500/30">
            <p className="text-red-400">{error}</p>
          </div>
        )}
        
        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="glass rounded-xl p-6 h-64">
                <div className="shimmer h-6 w-2/3 rounded mb-4" />
                <div className="shimmer h-4 w-1/3 rounded mb-6" />
                <div className="shimmer h-12 w-full rounded mb-4" />
                <div className="shimmer h-8 w-full rounded" />
              </div>
            ))}
          </div>
        )}
        
        {/* Search Results */}
        {!loading && results.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.map((result) => (
              <ComparisonCard
                key={result.product_id}
                product={result}
                onClick={() => setSelectedProduct(result)}
                onQuickOrder={() => setQuickOrderProduct(result)}
                onOneClickCheckout={() => setSmartCheckoutProduct(result)}
                onNegotiate={() => setNegotiateProduct(result)}
                isSelected={selectedProduct?.product_id === result.product_id}
              />
            ))}
          </div>
        )}
        
        {/* Deals Section (when no search) */}
        {showDeals && !loading && (
          <DealsSection 
            apiUrl={API_URL} 
            onOneClickCheckout={(deal) => {
              // Convert deal to product-like structure for checkout
              const productForCheckout: SearchResult = {
                product_id: deal.product_id,
                product_name: deal.product_name,
                brand: deal.brand,
                category: deal.category,
                quantity: deal.quantity,
                image_url: null,
                lowest_price: deal.best_price,
                highest_price: deal.highest_price,
                savings_percent: deal.savings_percent,
                best_platform: deal.best_platform_name,
                best_platform_logo: deal.best_platform_logo,
                best_delivery_time: deal.best_delivery_time,
                available_on: deal.available_on,
                prices: [{
                  platform: deal.best_platform,
                  platform_name: deal.best_platform_name,
                  platform_logo: deal.best_platform_logo,
                  price: deal.best_price,
                  mrp: deal.highest_price,
                  discount_percent: deal.savings_percent,
                  is_available: true,
                  delivery_time: deal.best_delivery_time,
                  url: ''
                }]
              };
              setSmartCheckoutProduct(productForCheckout);
            }}
          />
        )}
      </div>
      
      {/* Product Detail Modal */}
      {selectedProduct && (
        <ProductDetailModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
        />
      )}
      
      {/* Quick Order Modal */}
      {quickOrderProduct && (
        <QuickOrderModal
          product={quickOrderProduct}
          onClose={() => setQuickOrderProduct(null)}
          userLocation={{ city: currentLocation.city, pincode: currentLocation.pincode }}
        />
      )}
      
      {/* One-Click Checkout */}
      {checkoutProduct && (
        <OneClickCheckout
          product={checkoutProduct}
          onClose={() => setCheckoutProduct(null)}
          userLocation={{ city: currentLocation.city, pincode: currentLocation.pincode }}
        />
      )}
      
      {/* Smart Checkout (Faster Flow) */}
      {smartCheckoutProduct && (
        <SmartCheckout
          product={smartCheckoutProduct}
          onClose={() => setSmartCheckoutProduct(null)}
          userLocation={{ city: currentLocation.city, pincode: currentLocation.pincode }}
        />
      )}
      
      {/* Negotiate Modal */}
      {negotiateProduct && (
        <NegotiateModal
          product={negotiateProduct}
          onClose={() => setNegotiateProduct(null)}
          onSuccess={(offerId) => {
            console.log('Offer created:', offerId);
          }}
        />
      )}
      
      {/* AI Chatbot */}
      <Chatbot 
        onSearch={(query) => handleSearch(query)}
        onShowDeals={() => {
          setShowDeals(true);
          setResults([]);
          setSearchQuery('');
        }}
        onQuickOrder={async (query) => {
          // Search and open quick order for first result
          try {
            const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            if (data.results && data.results.length > 0) {
              setQuickOrderProduct(data.results[0]);
            } else {
              handleSearch(query); // Fallback to regular search
            }
          } catch {
            handleSearch(query);
          }
        }}
        onBuyNow={async (query) => {
          // Search and redirect to best platform
          try {
            const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            if (data.results && data.results.length > 0) {
              const product = data.results[0];
              const bestPrice = product.prices.find((p: { price: number; is_available: boolean }) => 
                p.price === product.lowest_price && p.is_available
              );
              if (bestPrice?.url) {
                window.open(bestPrice.url, '_blank');
              } else {
                setQuickOrderProduct(product);
              }
            } else {
              handleSearch(query);
            }
          } catch {
            handleSearch(query);
          }
        }}
        onOneClickCheckout={async (query) => {
          // Search and open smart checkout for first result
          try {
            const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            if (data.results && data.results.length > 0) {
              setSmartCheckoutProduct(data.results[0]);
            } else {
              handleSearch(query);
            }
          } catch {
            handleSearch(query);
          }
        }}
        onNegotiate={async (query) => {
          // Search and open negotiate modal for first result
          try {
            const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            if (data.results && data.results.length > 0) {
              setNegotiateProduct(data.results[0]);
            } else {
              handleSearch(query);
            }
          } catch {
            handleSearch(query);
          }
        }}
      />
      
      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>
            🛒 Quick Commerce Price Comparison | Compare prices across Indian quick commerce platforms
          </p>
          <p className="mt-2">
            Built for the AI Technology Workshop
          </p>
        </div>
      </footer>
    </main>
  );
}

// Product Detail Modal Component
function ProductDetailModal({ 
  product, 
  onClose 
}: { 
  product: SearchResult; 
  onClose: () => void;
}) {
  return (
    <div 
      className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="glass rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-white/10">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="font-display text-2xl font-bold">{product.product_name}</h2>
              <div className="flex items-center gap-2 mt-2">
                {product.brand && (
                  <span className="text-sm text-gray-400">{product.brand}</span>
                )}
                <span className="text-sm text-gray-500">•</span>
                <span className="text-sm text-gray-400">{product.quantity}</span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Price Summary */}
          <div className="mt-6 flex items-center gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary price-tag">₹{product.lowest_price}</div>
              <div className="text-xs text-gray-500 mt-1">Lowest</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-semibold text-gray-400">₹{product.highest_price}</div>
              <div className="text-xs text-gray-500 mt-1">Highest</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-semibold text-accent">
                Save ₹{(product.highest_price - product.lowest_price).toFixed(0)}
              </div>
              <div className="text-xs text-gray-500 mt-1">{product.savings_percent.toFixed(0)}% savings</div>
            </div>
          </div>
        </div>
        
        {/* Price Comparison Table */}
        <div className="p-6">
          <h3 className="text-lg font-semibold mb-4">Price Comparison</h3>
          <div className="space-y-3">
            {product.prices
              .sort((a, b) => a.price - b.price)
              .map((price, index) => (
                <div
                  key={price.platform}
                  className={`p-4 rounded-xl ${
                    index === 0 ? 'bg-primary/20 border border-primary/30 deal-pulse' : 'glass'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{price.platform_logo}</span>
                      <div>
                        <div className="font-semibold">{price.platform_name}</div>
                        <div className="text-sm text-gray-400">
                          {price.is_available ? price.delivery_time : 'Out of Stock'}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-xl font-bold ${index === 0 ? 'text-primary' : ''}`}>
                        ₹{price.price}
                      </div>
                      {price.mrp > price.price && (
                        <div className="text-sm">
                          <span className="text-gray-500 line-through">₹{price.mrp}</span>
                          <span className="text-green-400 ml-2">{price.discount_percent.toFixed(0)}% off</span>
                        </div>
                      )}
                      {index === 0 && (
                        <div className="mt-1">
                          <span className="bg-primary/30 text-primary text-xs px-2 py-0.5 rounded-full">
                            Best Price
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Buy Button for each platform */}
                  <div className="mt-3">
                    <a
                      href={price.url || `https://www.${price.platform}.com`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`w-full py-2.5 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
                        index === 0 
                          ? 'bg-primary hover:bg-primary/80 text-white' 
                          : price.is_available 
                            ? 'bg-white/10 hover:bg-white/20 text-white'
                            : 'bg-gray-600/50 text-gray-400 cursor-not-allowed'
                      }`}
                      onClick={(e) => !price.is_available && e.preventDefault()}
                    >
                      {price.is_available ? (
                        <>
                          <span>🛒</span>
                          {index === 0 ? 'Buy Now - Best Price!' : `Buy on ${price.platform_name}`}
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </>
                      ) : (
                        'Out of Stock'
                      )}
                    </a>
                  </div>
                </div>
              ))}
          </div>
          
          {/* Quick Buy Best Price Button */}
          <div className="mt-6 p-4 bg-gradient-to-r from-primary/20 to-secondary/20 rounded-xl border border-primary/30">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="font-semibold">🏆 Best Deal</div>
                <div className="text-sm text-gray-400">
                  {product.best_platform} • {product.best_delivery_time}
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-primary">₹{product.lowest_price}</div>
                <div className="text-xs text-gray-400">
                  Save ₹{(product.highest_price - product.lowest_price).toFixed(0)}
                </div>
              </div>
            </div>
            <a
              href={product.prices.find(p => p.price === product.lowest_price && p.is_available)?.url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full py-3 bg-primary hover:bg-primary/80 rounded-xl font-bold transition-colors flex items-center justify-center gap-2 text-lg"
            >
              <span>🛒</span>
              Buy Now @ ₹{product.lowest_price}
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

