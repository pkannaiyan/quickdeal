'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

interface BuyerStats {
  total_offers_made: number;
  offers_accepted: number;
  offers_rejected: number;
  offers_pending: number;
  offers_countered: number;
  total_deals: number;
  total_spent: number;
  total_savings: number;
  avg_discount: number;
  success_rate: number;
}

interface Offer {
  offer_id: string;
  product_name: string;
  product_quantity: string;
  platform: string;
  platform_name: string;
  original_price: number;
  offered_price: number;
  discount_percent: number;
  quantity: number;
  total_offered: number;
  status: string;
  counter_price?: number;
  counter_message?: string;
  created_at: string;
}

interface Deal {
  deal_id: string;
  product_name: string;
  platform: string;
  platform_name?: string;
  original_price: number;
  final_price: number;
  quantity: number;
  total_amount: number;
  savings: number;
  savings_percent: number;
  status: string;
  created_at: string;
}

// Platform URLs for buying
const PLATFORM_URLS: Record<string, string> = {
  'blinkit': 'https://blinkit.com/s?q=',
  'zepto': 'https://www.zeptonow.com/search?query=',
  'jiomart': 'https://www.jiomart.com/search?q=',
  'bigbasket': 'https://www.bigbasket.com/ps/?q=',
  'instamart': 'https://www.swiggy.com/instamart/search?query=',
};

// Platform app deep links
const PLATFORM_APPS: Record<string, { name: string; color: string; appLink: string; webLink: string }> = {
  'blinkit': {
    name: 'Blinkit',
    color: 'from-yellow-500 to-yellow-600',
    appLink: 'blinkit://',
    webLink: 'https://blinkit.com'
  },
  'zepto': {
    name: 'Zepto',
    color: 'from-purple-500 to-purple-600',
    appLink: 'zepto://',
    webLink: 'https://www.zeptonow.com'
  },
  'jiomart': {
    name: 'JioMart',
    color: 'from-blue-500 to-blue-600',
    appLink: 'jiomart://',
    webLink: 'https://www.jiomart.com'
  },
  'bigbasket': {
    name: 'BigBasket',
    color: 'from-green-500 to-green-600',
    appLink: 'bigbasket://',
    webLink: 'https://www.bigbasket.com'
  },
  'instamart': {
    name: 'Swiggy Instamart',
    color: 'from-orange-500 to-orange-600',
    appLink: 'swiggy://',
    webLink: 'https://www.swiggy.com/instamart'
  },
};

export default function BuyerDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<BuyerStats | null>(null);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'offers' | 'deals'>('overview');
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showUserIdInput, setShowUserIdInput] = useState(false);
  const [customUserId, setCustomUserId] = useState('');
  
  // One-Click Buy modal state
  const [oneClickDeal, setOneClickDeal] = useState<Deal | null>(null);
  const [copied, setCopied] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [orderProcessing, setOrderProcessing] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const storedUserId = localStorage.getItem('userId');
    const storedRole = localStorage.getItem('userRole');
    const storedName = localStorage.getItem('userName');
    
    if (storedUserId && (storedRole === 'buyer' || storedRole === 'admin')) {
      setUserId(storedUserId);
      setUserName(storedName || 'Buyer');
      setIsLoggedIn(true);
    } else if (storedUserId) {
      // Allow access even without explicit role for demo
      setUserId(storedUserId);
      setUserName(storedName || 'Guest Buyer');
      setIsLoggedIn(true);
    } else {
      // Create a demo buyer ID for guests
      const demoId = `buyer_${Date.now()}`;
      localStorage.setItem('userId', demoId);
      localStorage.setItem('userRole', 'buyer');
      localStorage.setItem('userName', 'Guest Buyer');
      setUserId(demoId);
      setUserName('Guest Buyer');
      setIsLoggedIn(true);
    }
  }, [router]);

  useEffect(() => {
    if (userId) {
      fetchData();
      
      // Auto refresh every 5 seconds
      const interval = setInterval(fetchData, 5000);
      return () => clearInterval(interval);
    }
  }, [userId]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const headers = {
        'Content-Type': 'application/json',
        'X-User-Id': userId,
        'X-User-Name': localStorage.getItem('userName') || 'Guest Buyer'
      };

      const [statsRes, offersRes, dealsRes] = await Promise.all([
        fetch(`${API_URL}/api/negotiate/buyer/stats`, { headers }),
        fetch(`${API_URL}/api/negotiate/offers/my`, { headers }),
        fetch(`${API_URL}/api/negotiate/buyer/deals`, { headers })
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData.stats);
      }

      if (offersRes.ok) {
        const offersData = await offersRes.json();
        setOffers(offersData.offers);
      }

      if (dealsRes.ok) {
        const dealsData = await dealsRes.json();
        setDeals(dealsData.deals);
      }
    } catch (e) {
      console.error('Fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptCounter = async (offerId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/negotiate/offers/${offerId}/accept-counter`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId
        }
      });

      if (response.ok) {
        fetchData();
      }
    } catch (e) {
      console.error('Accept counter error:', e);
    }
  };

  const handleRejectCounter = async (offerId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/negotiate/offers/${offerId}/reject-counter`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId
        }
      });

      if (response.ok) {
        fetchData();
      }
    } catch (e) {
      console.error('Reject counter error:', e);
    }
  };

  const handleCancelOffer = async (offerId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/negotiate/offers/${offerId}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId
        }
      });

      if (response.ok) {
        fetchData();
      }
    } catch (e) {
      console.error('Cancel offer error:', e);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'accepted': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'rejected': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'countered': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'completed': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Place order at the negotiated deal price
  const placeOrderAtDealPrice = async (deal: Deal) => {
    setOrderProcessing(true);
    try {
      // Track the order at the negotiated price
      await fetch(`${API_URL}/api/analytics/track/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: deal.deal_id,
          product_name: deal.product_name,
          selected_platform: deal.platform,
          price: deal.final_price,  // Use the negotiated deal price
          original_price: deal.original_price,
          quantity: deal.quantity,
          order_type: 'negotiated_deal',
          deal_reference: deal.deal_id,
          savings: deal.savings,
          all_prices: [
            { 
              platform: deal.platform, 
              price: deal.final_price,  // Deal price, not market price
              is_available: true,
              is_negotiated: true
            }
          ]
        })
      });

      // Update deal status to "ordered"
      await fetch(`${API_URL}/api/negotiate/deals/${deal.deal_id}/order`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-User-Id': userId
        },
        body: JSON.stringify({
          order_price: deal.final_price,
          quantity: deal.quantity
        })
      });

      setOrderPlaced(true);
      setCurrentStep(4);
      
      // Refresh deals after ordering
      setTimeout(() => {
        fetchData();
      }, 2000);
      
    } catch (error) {
      console.error('Failed to place order:', error);
    } finally {
      setOrderProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900">
      {/* Header */}
      <header className="glass border-b border-white/10 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-gray-400 hover:text-white">
              ← Back
            </Link>
            <div>
              <h1 className="text-2xl font-bold">
                <span className="bg-gradient-to-r from-[#00D9A5] to-[#00B894] bg-clip-text text-transparent">QuickDeal</span>
                <span className="text-white ml-2">| Buyer</span>
              </h1>
              <p className="text-gray-400 text-sm">Your negotiations, deals & orders</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* User ID Display & Switcher */}
            <div className="relative">
              <button
                onClick={() => setShowUserIdInput(!showUserIdInput)}
                className="text-xs px-2 py-1 bg-purple-500/20 text-purple-400 rounded hover:bg-purple-500/30"
                title="Click to switch user"
              >
                ID: {userId.slice(0, 12)}...
              </button>
              
              {showUserIdInput && (
                <div className="absolute right-0 top-full mt-2 p-3 glass rounded-lg border border-white/10 z-50 w-64">
                  <p className="text-xs text-gray-400 mb-2">Current User ID:</p>
                  <p className="text-xs font-mono text-purple-400 mb-3 break-all">{userId}</p>
                  
                  <p className="text-xs text-gray-400 mb-2">Switch to demo user:</p>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={customUserId}
                      onChange={(e) => setCustomUserId(e.target.value)}
                      placeholder="Enter user ID"
                      className="flex-1 text-xs bg-white/10 border border-white/10 rounded px-2 py-1"
                    />
                    <button
                      onClick={() => {
                        if (customUserId) {
                          localStorage.setItem('userId', customUserId);
                          setUserId(customUserId);
                          setShowUserIdInput(false);
                        }
                      }}
                      className="px-2 py-1 bg-purple-500 rounded text-xs"
                    >
                      Switch
                    </button>
                  </div>
                  
                  <p className="text-xs text-gray-500 mb-2">Quick switch:</p>
                  <div className="flex flex-wrap gap-1">
                    {['test_demo_buyer_123', 'buyer_1765004921575', 'john_buyer', 'mary_buyer'].map((id) => (
                      <button
                        key={id}
                        onClick={() => {
                          localStorage.setItem('userId', id);
                          setUserId(id);
                          setShowUserIdInput(false);
                        }}
                        className="text-[10px] px-2 py-0.5 bg-white/10 hover:bg-white/20 rounded"
                      >
                        {id.slice(0, 15)}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <span className="text-gray-400 text-sm">👋 {userName}</span>
            <Link 
              href="/seller"
              className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm"
            >
              Seller →
            </Link>
            <button
              onClick={() => {
                localStorage.removeItem('userId');
                localStorage.removeItem('userRole');
                localStorage.removeItem('userName');
                router.push('/login');
              }}
              className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-purple-400">{stats.total_offers_made}</div>
              <div className="text-sm text-gray-400">Total Offers</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-yellow-400">{stats.offers_pending}</div>
              <div className="text-sm text-gray-400">Pending</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-green-400">{stats.offers_accepted}</div>
              <div className="text-sm text-gray-400">Accepted</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-blue-400">{stats.offers_countered}</div>
              <div className="text-sm text-gray-400">Countered</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-emerald-400">₹{stats.total_savings.toFixed(0)}</div>
              <div className="text-sm text-gray-400">Total Savings</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-pink-400">{stats.success_rate.toFixed(0)}%</div>
              <div className="text-sm text-gray-400">Success Rate</div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {(['overview', 'offers', 'deals'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === tab
                  ? 'bg-purple-500 text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full" />
          </div>
        ) : (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="grid md:grid-cols-2 gap-6">
                {/* Recent Offers */}
                <div className="glass rounded-xl p-6">
                  <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
                    📝 Recent Offers
                    <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-full">
                      {offers.length}
                    </span>
                  </h2>
                  <div className="space-y-3">
                    {offers.slice(0, 5).map((offer) => (
                      <div key={offer.offer_id} className="bg-white/5 rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div className="font-medium text-sm line-clamp-1">{offer.product_name}</div>
                          <span className={`text-[10px] px-2 py-0.5 rounded border ${getStatusColor(offer.status)}`}>
                            {offer.status.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] px-1.5 py-0.5 bg-indigo-500/20 text-indigo-400 rounded">
                            🌐 {offer.platform_name || offer.platform}
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Offered: ₹{offer.offered_price}</span>
                          <span className="text-green-400">-{offer.discount_percent.toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                    {offers.length === 0 && (
                      <p className="text-gray-500 text-center py-8">No offers yet. Start negotiating!</p>
                    )}
                  </div>
                </div>

                {/* Recent Deals */}
                <div className="glass rounded-xl p-6">
                  <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
                    ✅ Recent Deals
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                      {deals.length}
                    </span>
                  </h2>
                  <div className="space-y-3">
                    {deals.slice(0, 5).map((deal) => (
                      <div key={deal.deal_id} className="bg-white/5 rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div className="font-medium text-sm line-clamp-1">{deal.product_name}</div>
                          <span className="text-green-400 font-bold">₹{deal.final_price}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Saved ₹{deal.savings.toFixed(0)}</span>
                          <span className="text-emerald-400">{deal.savings_percent.toFixed(0)}% off</span>
                        </div>
                      </div>
                    ))}
                    {deals.length === 0 && (
                      <p className="text-gray-500 text-center py-8">No deals completed yet.</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Offers Tab */}
            {activeTab === 'offers' && (
              <div className="space-y-4">
                {offers.map((offer) => (
                  <div key={offer.offer_id} className="glass rounded-xl p-5">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-start gap-3 mb-2">
                          <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center text-xl">
                            🛍️
                          </div>
                          <div>
                            <h3 className="font-semibold">{offer.product_name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded-full">
                                🌐 {offer.platform_name || offer.platform}
                              </span>
                            </div>
                            <div className="text-sm text-gray-400 mt-1">
                              {offer.product_quantity} × {offer.quantity}
                            </div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4 mt-4">
                          <div>
                            <div className="text-xs text-gray-500">Original Price</div>
                            <div className="text-gray-400 line-through">₹{offer.original_price}</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Your Offer</div>
                            <div className="text-green-400 font-bold">₹{offer.offered_price}</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Discount</div>
                            <div className="text-purple-400">{offer.discount_percent.toFixed(0)}%</div>
                          </div>
                        </div>

                        {offer.status === 'countered' && offer.counter_price && (
                          <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-blue-400">💬</span>
                              <span className="font-medium text-blue-400">Counter Offer Received!</span>
                            </div>
                            <div className="text-lg font-bold text-white">₹{offer.counter_price}</div>
                            {offer.counter_message && (
                              <p className="text-sm text-gray-400 mt-1">{offer.counter_message}</p>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="flex flex-col gap-2">
                        <span className={`px-3 py-1 rounded-lg border text-center text-sm ${getStatusColor(offer.status)}`}>
                          {offer.status.toUpperCase()}
                        </span>
                        
                        {offer.status === 'countered' && (
                          <>
                            <button
                              onClick={() => handleAcceptCounter(offer.offer_id)}
                              className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg text-sm font-medium"
                            >
                              Accept ₹{offer.counter_price}
                            </button>
                            <button
                              onClick={() => handleRejectCounter(offer.offer_id)}
                              className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm"
                            >
                              Reject
                            </button>
                          </>
                        )}

                        {offer.status === 'pending' && (
                          <button
                            onClick={() => handleCancelOffer(offer.offer_id)}
                            className="px-4 py-2 bg-gray-500/20 hover:bg-gray-500/30 text-gray-400 rounded-lg text-sm"
                          >
                            Cancel
                          </button>
                        )}

                        {/* One-Click Buy for accepted/completed offers */}
                        {(offer.status === 'accepted' || offer.status === 'completed') && (
                          <button
                            onClick={() => {
                              // Create a deal-like object from the offer
                              setOneClickDeal({
                                deal_id: offer.offer_id,
                                product_name: offer.product_name,
                                platform: offer.platform,
                                platform_name: offer.platform_name,
                                original_price: offer.original_price,
                                final_price: offer.offered_price,
                                quantity: offer.quantity,
                                total_amount: offer.total_offered,
                                savings: (offer.original_price - offer.offered_price) * offer.quantity,
                                savings_percent: offer.discount_percent,
                                status: offer.status,
                                created_at: offer.created_at
                              });
                              setCurrentStep(1);
                              setCopied(false);
                            }}
                            className={`px-4 py-2 bg-gradient-to-r ${PLATFORM_APPS[offer.platform]?.color || 'from-green-500 to-emerald-500'} hover:opacity-90 rounded-lg font-bold text-sm flex items-center gap-2`}
                          >
                            ⚡ One-Click Buy @ ₹{offer.offered_price}
                          </button>
                        )}

                        <div className="text-xs text-gray-500 text-center">
                          {formatDate(offer.created_at)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {offers.length === 0 && (
                  <div className="glass rounded-xl p-12 text-center">
                    <div className="text-4xl mb-4">🤝</div>
                    <h3 className="text-xl font-bold mb-2">No Offers Yet</h3>
                    <p className="text-gray-400 mb-4">Start negotiating for better prices!</p>
                    <Link href="/" className="px-6 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg inline-block">
                      Browse Products
                    </Link>
                  </div>
                )}
              </div>
            )}

            {/* Deals Tab */}
            {activeTab === 'deals' && (
              <div className="space-y-4">
                {/* Info Banner */}
                <div className="glass rounded-xl p-4 border-l-4 border-green-500">
                  <p className="text-green-400 font-medium">
                    🎉 Your negotiated deals! Click "Buy Now" to purchase at your agreed price.
                  </p>
                </div>

                {deals.map((deal) => (
                  <div key={deal.deal_id} className="glass rounded-xl p-5">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex items-start gap-3">
                        <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center text-xl">
                          ✅
                        </div>
                        <div>
                          <h3 className="font-semibold">{deal.product_name}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded-full">
                              🌐 {deal.platform_name || deal.platform}
                            </span>
                          </div>
                          <div className="text-xs text-gray-500 mt-1">{formatDate(deal.created_at)}</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-6">
                        <div className="text-center">
                          <div className="text-xs text-gray-500">Original</div>
                          <div className="text-gray-400 line-through">₹{deal.original_price}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-gray-500">Final Price</div>
                          <div className="text-green-400 font-bold">₹{deal.final_price}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-gray-500">You Saved</div>
                          <div className="text-emerald-400 font-bold">₹{deal.savings.toFixed(0)}</div>
                          <div className="text-xs text-emerald-400">({deal.savings_percent.toFixed(0)}%)</div>
                        </div>
                      </div>

                      <div className="flex flex-col gap-2 items-end">
                        <span className={`px-3 py-1 rounded-lg border text-sm ${getStatusColor(deal.status)}`}>
                          {deal.status.replace('_', ' ').toUpperCase()}
                        </span>
                        
                        {/* One-Click Buy Button */}
                        <button
                          onClick={() => {
                            setOneClickDeal(deal);
                            setCurrentStep(1);
                            setCopied(false);
                          }}
                          className={`px-4 py-2 bg-gradient-to-r ${PLATFORM_APPS[deal.platform]?.color || 'from-green-500 to-emerald-500'} hover:opacity-90 rounded-lg font-bold text-sm flex items-center gap-2 transition-all shadow-lg`}
                        >
                          ⚡ One-Click Buy @ ₹{deal.final_price}
                        </button>
                        
                        {/* Quick Search Link */}
                        <a
                          href={`${PLATFORM_URLS[deal.platform] || PLATFORM_URLS['jiomart']}${encodeURIComponent(deal.product_name)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-indigo-400 hover:text-indigo-300"
                        >
                          🔗 Search on {PLATFORM_APPS[deal.platform]?.name || deal.platform}
                        </a>
                        
                        {/* Deal Code */}
                        <div className="text-xs text-gray-500">
                          Deal: {deal.deal_id.slice(0, 8).toUpperCase()}
                        </div>
                      </div>
                    </div>
                    
                    {/* Price Summary */}
                    <div className="mt-4 pt-4 border-t border-white/10">
                      <div className="flex justify-between items-center">
                        <div className="text-sm text-gray-400">
                          Original: <span className="line-through">₹{deal.original_price}</span>
                        </div>
                        <div className="text-sm">
                          <span className="text-green-400 font-bold">You saved ₹{deal.savings.toFixed(0)}</span>
                          <span className="text-gray-500 ml-2">({deal.savings_percent.toFixed(0)}% off)</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {deals.length === 0 && (
                  <div className="glass rounded-xl p-12 text-center">
                    <div className="text-4xl mb-4">📦</div>
                    <h3 className="text-xl font-bold mb-2">No Deals Yet</h3>
                    <p className="text-gray-400">Your completed deals will appear here</p>
                    <Link href="/" className="mt-4 inline-block px-4 py-2 bg-purple-500 rounded-lg text-sm">
                      Start Negotiating →
                    </Link>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>

      {/* One-Click Buy Modal */}
      {oneClickDeal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="glass rounded-2xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-xl font-bold flex items-center gap-2">
                  ⚡ One-Click Buy
                </h2>
                <p className="text-gray-400 text-sm mt-1">Complete your purchase in 3 easy steps</p>
              </div>
              <button
                onClick={() => setOneClickDeal(null)}
                className="p-2 hover:bg-white/10 rounded-lg"
              >
                ✕
              </button>
            </div>

            {/* Deal Summary */}
            <div className={`bg-gradient-to-r ${PLATFORM_APPS[oneClickDeal.platform]?.color || 'from-green-500 to-emerald-500'} rounded-xl p-4 mb-6`}>
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-bold text-lg">{oneClickDeal.product_name}</div>
                  <div className="text-white/80 text-sm">{PLATFORM_APPS[oneClickDeal.platform]?.name || oneClickDeal.platform}</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">₹{oneClickDeal.final_price}</div>
                  <div className="text-white/80 text-sm line-through">₹{oneClickDeal.original_price}</div>
                </div>
              </div>
              <div className="mt-2 text-center bg-white/20 rounded-lg py-1 text-sm font-medium">
                🎉 You saved ₹{oneClickDeal.savings.toFixed(0)} ({oneClickDeal.savings_percent.toFixed(0)}% off)
              </div>
            </div>

            {/* Steps */}
            <div className="space-y-4">
              {/* Step 1: Copy Product */}
              <div className={`p-4 rounded-xl border ${currentStep >= 1 ? 'bg-white/5 border-white/20' : 'border-white/10 opacity-50'}`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${currentStep >= 1 ? 'bg-purple-500' : 'bg-gray-600'}`}>
                    1
                  </div>
                  <div className="font-medium">Copy Product Details</div>
                </div>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(`${oneClickDeal.product_name} - ₹${oneClickDeal.final_price} (Deal: ${oneClickDeal.deal_id.slice(0, 8).toUpperCase()})`);
                    setCopied(true);
                    setCurrentStep(2);
                    setTimeout(() => setCopied(false), 3000);
                  }}
                  className={`w-full py-3 rounded-lg font-medium transition-all ${
                    copied 
                      ? 'bg-green-500 text-white' 
                      : 'bg-white/10 hover:bg-white/20'
                  }`}
                >
                  {copied ? '✓ Copied to Clipboard!' : '📋 Copy Product Name & Price'}
                </button>
              </div>

              {/* Step 2: Open App */}
              <div className={`p-4 rounded-xl border ${currentStep >= 2 ? 'bg-white/5 border-white/20' : 'border-white/10 opacity-50'}`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${currentStep >= 2 ? 'bg-purple-500' : 'bg-gray-600'}`}>
                    2
                  </div>
                  <div className="font-medium">Open {PLATFORM_APPS[oneClickDeal.platform]?.name || oneClickDeal.platform}</div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <a
                    href={PLATFORM_APPS[oneClickDeal.platform]?.appLink || '#'}
                    onClick={() => setCurrentStep(3)}
                    className={`py-3 rounded-lg font-medium text-center bg-gradient-to-r ${PLATFORM_APPS[oneClickDeal.platform]?.color || 'from-green-500 to-emerald-500'} hover:opacity-90`}
                  >
                    📱 Open App
                  </a>
                  <a
                    href={`${PLATFORM_URLS[oneClickDeal.platform] || PLATFORM_URLS['jiomart']}${encodeURIComponent(oneClickDeal.product_name)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={() => setCurrentStep(3)}
                    className="py-3 rounded-lg font-medium text-center bg-white/10 hover:bg-white/20"
                  >
                    🌐 Open Website
                  </a>
                </div>
              </div>

              {/* Step 3: Complete Purchase */}
              <div className={`p-4 rounded-xl border ${currentStep >= 3 ? 'bg-white/5 border-white/20' : 'border-white/10 opacity-50'}`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${currentStep >= 3 ? 'bg-purple-500' : 'bg-gray-600'}`}>
                    3
                  </div>
                  <div className="font-medium">Complete Purchase</div>
                </div>
                <div className="text-sm text-gray-400 space-y-2">
                  <p>✓ Search for the product in the app/website</p>
                  <p>✓ Add to cart at the negotiated price: <span className="text-green-400 font-bold">₹{oneClickDeal.final_price}</span></p>
                  <p>✓ Complete checkout with your saved address</p>
                </div>
              </div>
            </div>

            {/* Confirm Order at Deal Price */}
            {!orderPlaced ? (
              <div className="mt-6 space-y-3">
                <div className="p-4 bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl">
                  <div className="text-center mb-3">
                    <div className="text-sm text-gray-400">Your Negotiated Price</div>
                    <div className="text-3xl font-bold text-green-400">₹{oneClickDeal.final_price}</div>
                    <div className="text-xs text-gray-500 line-through">Original: ₹{oneClickDeal.original_price}</div>
                  </div>
                  
                  <button
                    onClick={() => placeOrderAtDealPrice(oneClickDeal)}
                    disabled={orderProcessing}
                    className={`w-full py-4 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 rounded-xl font-bold text-lg flex items-center justify-center gap-2 shadow-lg shadow-green-500/30 transition-all ${orderProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {orderProcessing ? (
                      <>
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Processing...
                      </>
                    ) : (
                      <>
                        ✓ Confirm Order @ ₹{oneClickDeal.final_price}
                      </>
                    )}
                  </button>
                  
                  <p className="text-center text-xs text-gray-500 mt-2">
                    Order will be placed at your negotiated deal price
                  </p>
                </div>

                {/* Deal Reference */}
                <div className="p-3 bg-white/5 rounded-lg text-center">
                  <div className="text-xs text-gray-500">Deal Reference</div>
                  <div className="font-mono text-sm text-yellow-400">{oneClickDeal.deal_id.slice(0, 8).toUpperCase()}</div>
                </div>
              </div>
            ) : (
              <div className="mt-6 p-6 bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl text-center">
                <div className="text-5xl mb-3">🎉</div>
                <h3 className="text-xl font-bold text-green-400 mb-2">Order Placed Successfully!</h3>
                <p className="text-gray-400 mb-4">
                  Your order for <span className="font-semibold text-white">{oneClickDeal.product_name}</span> has been placed at <span className="font-bold text-green-400">₹{oneClickDeal.final_price}</span>
                </p>
                <div className="p-3 bg-black/20 rounded-lg mb-4">
                  <div className="text-xs text-gray-500">Order Reference</div>
                  <div className="font-mono text-lg text-yellow-400">{oneClickDeal.deal_id.slice(0, 8).toUpperCase()}</div>
                </div>
                <div className="text-sm text-gray-500">
                  You saved <span className="font-bold text-green-400">₹{oneClickDeal.savings.toFixed(0)}</span> with this negotiated deal!
                </div>
              </div>
            )}

            {/* Close Button */}
            <button
              onClick={() => {
                setOneClickDeal(null);
                setOrderPlaced(false);
                setCurrentStep(1);
              }}
              className="mt-4 w-full py-3 bg-white/10 hover:bg-white/20 rounded-lg font-medium"
            >
              {orderPlaced ? 'Done' : 'Close'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

