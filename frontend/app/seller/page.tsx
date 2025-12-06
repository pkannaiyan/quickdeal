'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

interface SellerInfo {
  seller_id: string;
  business_name: string;
  platform: string;
  platform_name: string;
  manual_review_only: boolean;
  manual_review_timeout_mins: number;
  auto_accept_discount: number;
  auto_reject_discount: number;
  max_discount: number;
}

interface SellerStats {
  total_offers_received: number;
  offers_accepted: number;
  offers_rejected: number;
  offers_pending: number;
  offers_countered: number;
  total_deals: number;
  total_revenue: number;
  avg_deal_value: number;
  avg_discount_given: number;
  response_rate: number;
  acceptance_rate: number;
  top_products: Array<{ name: string; count: number; revenue: number }>;
}

interface PendingOffer {
  offer_id: string;
  product_name: string;
  product_quantity: string;
  buyer_name: string;
  platform: string;
  platform_name: string;
  original_price: number;
  offered_price: number;
  discount_percent: number;
  quantity: number;
  total_offered: number;
  message?: string;
  pincode?: string;
  city?: string;
  created_at: string;
  expires_at?: string;
  manual_review_deadline?: string;
  time_remaining_secs?: number;
}

interface Deal {
  deal_id: string;
  product_name: string;
  buyer_name: string;
  platform: string;
  platform_name: string;
  original_price: number;
  final_price: number;
  quantity: number;
  total_amount: number;
  savings_percent: number;
  status: string;
  created_at: string;
}

export default function SellerDashboard() {
  const router = useRouter();
  const [seller, setSeller] = useState<SellerInfo | null>(null);
  const [stats, setStats] = useState<SellerStats | null>(null);
  const [pendingOffers, setPendingOffers] = useState<PendingOffer[]>([]);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'offers' | 'deals' | 'settings'>('overview');
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string>('');
  const [userName, setUserName] = useState<string>('');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('blinkit');
  
  const platforms = [
    { id: 'blinkit', name: 'Blinkit', userId: 'user_blinkit' },
    { id: 'zepto', name: 'Zepto', userId: 'user_zepto' },
    { id: 'jiomart', name: 'JioMart', userId: 'user_jiomart' },
    { id: 'bigbasket', name: 'BigBasket', userId: 'user_bigbasket' },
    { id: 'instamart', name: 'Swiggy Instamart', userId: 'user_instamart' },
  ];
  
  // Settings state
  const [manualReviewOnly, setManualReviewOnly] = useState(false);
  const [manualReviewTimeout, setManualReviewTimeout] = useState(5);
  const [autoAcceptDiscount, setAutoAcceptDiscount] = useState(10);
  const [autoRejectDiscount, setAutoRejectDiscount] = useState(30);
  const [maxDiscount, setMaxDiscount] = useState(30);
  
  // Timer state for countdown
  const [, setTimerTick] = useState(0);
  
  // Response modal
  const [respondingOffer, setRespondingOffer] = useState<PendingOffer | null>(null);
  const [counterPrice, setCounterPrice] = useState('');
  const [counterMessage, setCounterMessage] = useState('');

  // Set user ID based on selected platform
  useEffect(() => {
    const platform = platforms.find(p => p.id === selectedPlatform);
    if (platform) {
      setUserId(platform.userId);
      setUserName(`${platform.name} Seller`);
    }
  }, [selectedPlatform]);

  // Fetch data when userId is set
  useEffect(() => {
    if (!userId) return;
    
    fetchData();
    
    // Auto-refresh every 5 seconds to see new offers
    const refreshInterval = setInterval(() => {
      fetchData();
    }, 5000);
    
    return () => clearInterval(refreshInterval);
  }, [userId]);
  
  // Timer to update countdown every second
  useEffect(() => {
    const interval = setInterval(() => {
      setTimerTick(t => t + 1);
      // Also refresh data every 30 seconds to catch auto-processed offers
      if (Date.now() % 30000 < 1000) {
        fetchData();
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    if (!userId) return;
    
    setLoading(true);
    try {
      const headers = {
        'Content-Type': 'application/json',
        'X-User-Id': userId
      };

      console.log('Fetching seller data for:', userId);

      const [statsRes, pendingRes, dealsRes] = await Promise.all([
        fetch(`${API_URL}/api/negotiate/seller/stats`, { headers }),
        fetch(`${API_URL}/api/negotiate/seller/pending`, { headers }),
        fetch(`${API_URL}/api/negotiate/seller/deals`, { headers })
      ]);

      console.log('Stats response:', statsRes.status);
      console.log('Pending response:', pendingRes.status);
      console.log('Deals response:', dealsRes.status);

      if (statsRes.ok) {
        const data = await statsRes.json();
        console.log('Stats data:', data);
        setSeller(data.seller);
        setStats(data.stats);
        setManualReviewOnly(data.seller.manual_review_only ?? false);
        setManualReviewTimeout(data.seller.manual_review_timeout_mins ?? 5);
        setAutoAcceptDiscount(data.seller.auto_accept_discount ?? 10);
        setAutoRejectDiscount(data.seller.auto_reject_discount ?? 30);
        setMaxDiscount(data.seller.max_discount ?? 30);
      } else {
        console.error('Stats fetch failed:', await statsRes.text());
      }

      if (pendingRes.ok) {
        const data = await pendingRes.json();
        console.log('Pending offers:', data.pending_offers?.length);
        setPendingOffers(data.pending_offers || []);
      } else {
        console.error('Pending fetch failed:', await pendingRes.text());
      }

      if (dealsRes.ok) {
        const data = await dealsRes.json();
        console.log('Deals:', data.deals?.length);
        setDeals(data.deals || []);
      } else {
        console.error('Deals fetch failed:', await dealsRes.text());
      }
    } catch (e) {
      console.error('Fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (offerId: string, action: 'accept' | 'reject' | 'counter') => {
    try {
      const body: any = { action };
      
      if (action === 'counter') {
        if (!counterPrice) return;
        body.counter_price = parseFloat(counterPrice);
        body.message = counterMessage || undefined;
      }

      const response = await fetch(`${API_URL}/api/negotiate/seller/offers/${offerId}/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId
        },
        body: JSON.stringify(body)
      });

      if (response.ok) {
        setRespondingOffer(null);
        setCounterPrice('');
        setCounterMessage('');
        fetchData();
      }
    } catch (e) {
      console.error('Respond error:', e);
    }
  };

  const handleUpdateSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/negotiate/seller/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId
        },
        body: JSON.stringify({
          manual_review_only: manualReviewOnly,
          manual_review_timeout_mins: manualReviewTimeout,
          auto_accept_discount: autoAcceptDiscount,
          auto_reject_discount: autoRejectDiscount,
          max_discount: maxDiscount
        })
      });

      if (response.ok) {
        alert('Settings updated!');
        fetchData();
      }
    } catch (e) {
      console.error('Update settings error:', e);
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

  const getTimeRemaining = (expiresAt?: string) => {
    if (!expiresAt) return null;
    const diff = new Date(expiresAt).getTime() - Date.now();
    if (diff <= 0) return 'Expired';
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${mins}m`;
  };
  
  const getManualReviewTimeRemaining = (deadline?: string, secs?: number) => {
    // Use seconds from API if available, otherwise calculate
    let remainingSecs = secs;
    if (remainingSecs === undefined && deadline) {
      remainingSecs = Math.max(0, Math.floor((new Date(deadline).getTime() - Date.now()) / 1000));
    }
    if (remainingSecs === undefined || remainingSecs <= 0) {
      return { text: 'Auto-processing...', urgent: true, expired: true };
    }
    const mins = Math.floor(remainingSecs / 60);
    const secsLeft = remainingSecs % 60;
    return {
      text: `${mins}:${secsLeft.toString().padStart(2, '0')}`,
      urgent: remainingSecs < 60,
      expired: false
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900/20 to-slate-900">
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
                <span className="text-white ml-2">| Seller</span>
              </h1>
              <p className="text-gray-400 text-sm">
                {seller?.business_name || 'Loading...'} • {seller?.platform_name || ''}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* Platform Selector */}
            <select
              value={selectedPlatform}
              onChange={(e) => setSelectedPlatform(e.target.value)}
              className="bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-emerald-500"
            >
              {platforms.map((p) => (
                <option key={p.id} value={p.id} className="bg-slate-800">
                  {p.name}
                </option>
              ))}
            </select>
            
            {/* Manual Review Mode Badge */}
            {seller?.manual_review_only && (
              <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded-full">
                <span className="text-emerald-400">✋</span>
                <span className="text-emerald-400 text-sm font-medium">Manual Accept</span>
              </div>
            )}
            {pendingOffers.length > 0 && (
              <div className="flex items-center gap-2 px-3 py-1 bg-yellow-500/20 border border-yellow-500/30 rounded-full animate-pulse">
                <span className="text-yellow-400">🔔</span>
                <span className="text-yellow-400 text-sm font-medium">{pendingOffers.length} pending</span>
              </div>
            )}
            <div className="flex items-center gap-3">
              <span className="text-gray-400 text-sm">👋 {userName}</span>
              <Link 
                href="/buyer"
                className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm"
              >
                Buyer →
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
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats Overview */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-emerald-400">{stats.total_offers_received}</div>
              <div className="text-sm text-gray-400">Total Offers</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-yellow-400">{stats.offers_pending}</div>
              <div className="text-sm text-gray-400">Pending</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-green-400">{stats.acceptance_rate.toFixed(0)}%</div>
              <div className="text-sm text-gray-400">Accept Rate</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-blue-400">{stats.total_deals}</div>
              <div className="text-sm text-gray-400">Deals</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-purple-400">₹{stats.total_revenue.toFixed(0)}</div>
              <div className="text-sm text-gray-400">Revenue</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-pink-400">{stats.avg_discount_given.toFixed(1)}%</div>
              <div className="text-sm text-gray-400">Avg Discount</div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {(['overview', 'offers', 'deals', 'settings'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-all relative ${
                activeTab === tab
                  ? 'bg-emerald-500 text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {tab === 'offers' && pendingOffers.length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-xs flex items-center justify-center">
                  {pendingOffers.length}
                </span>
              )}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full" />
          </div>
        ) : (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="grid md:grid-cols-2 gap-6">
                {/* Pending Offers */}
                <div className="glass rounded-xl p-6">
                  <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
                    ⏳ Pending Offers
                    {pendingOffers.length > 0 && (
                      <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full animate-pulse">
                        Action Required
                      </span>
                    )}
                  </h2>
                  <div className="space-y-3">
                    {pendingOffers.slice(0, 5).map((offer) => {
                      const timer = getManualReviewTimeRemaining(offer.manual_review_deadline, offer.time_remaining_secs);
                      return (
                        <div key={offer.offer_id} className="bg-white/5 rounded-lg p-3">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <div className="font-medium text-sm line-clamp-1">{offer.product_name}</div>
                              <div className="text-xs text-gray-500">{offer.buyer_name}</div>
                              <div className="flex items-center gap-1 mt-1">
                                <span className="text-[10px] px-1.5 py-0.5 bg-indigo-500/20 text-indigo-400 rounded">
                                  🌐 {offer.platform_name || offer.platform}
                                </span>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-bold text-green-400">₹{offer.offered_price}</div>
                              <div className="text-xs text-red-400">-{offer.discount_percent.toFixed(0)}%</div>
                            </div>
                          </div>
                          {/* Timer */}
                          {!manualReviewOnly && (
                            <div className={`text-center py-1 mb-2 rounded text-xs font-mono ${
                              timer.expired 
                                ? 'bg-yellow-500/20 text-yellow-400 animate-pulse'
                                : timer.urgent 
                                ? 'bg-red-500/20 text-red-400 animate-pulse' 
                                : 'bg-blue-500/10 text-blue-400'
                            }`}>
                              ⏱️ {timer.text} {!timer.expired && 'to review'}
                            </div>
                          )}
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleRespond(offer.offer_id, 'accept')}
                              className="flex-1 py-1 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded text-xs"
                            >
                              Accept
                            </button>
                            <button
                              onClick={() => setRespondingOffer(offer)}
                              className="flex-1 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded text-xs"
                            >
                              Counter
                            </button>
                            <button
                              onClick={() => handleRespond(offer.offer_id, 'reject')}
                              className="flex-1 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded text-xs"
                            >
                              Reject
                            </button>
                          </div>
                        </div>
                      );
                    })}
                    {pendingOffers.length === 0 && (
                      <p className="text-gray-500 text-center py-8">No pending offers 🎉</p>
                    )}
                  </div>
                </div>

                {/* Top Products */}
                <div className="glass rounded-xl p-6">
                  <h2 className="font-bold text-lg mb-4">📊 Top Products</h2>
                  <div className="space-y-3">
                    {stats?.top_products.slice(0, 5).map((product, idx) => (
                      <div key={idx} className="bg-white/5 rounded-lg p-3 flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">
                            {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : '📦'}
                          </span>
                          <div>
                            <div className="font-medium text-sm line-clamp-1">{product.name}</div>
                            <div className="text-xs text-gray-500">{product.count} offers</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-emerald-400">₹{product.revenue.toFixed(0)}</div>
                        </div>
                      </div>
                    ))}
                    {(!stats?.top_products || stats.top_products.length === 0) && (
                      <p className="text-gray-500 text-center py-8">No data yet</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Offers Tab */}
            {activeTab === 'offers' && (
              <div className="space-y-4">
                {pendingOffers.map((offer) => {
                  const timer = getManualReviewTimeRemaining(offer.manual_review_deadline, offer.time_remaining_secs);
                  return (
                    <div key={offer.offer_id} className="glass rounded-xl p-5">
                      {/* Timer Banner */}
                      {!manualReviewOnly && (
                        <div className={`-mx-5 -mt-5 mb-4 px-5 py-3 rounded-t-xl flex items-center justify-between ${
                          timer.expired 
                            ? 'bg-yellow-500/20 border-b border-yellow-500/30'
                            : timer.urgent 
                            ? 'bg-red-500/20 border-b border-red-500/30 animate-pulse' 
                            : 'bg-blue-500/10 border-b border-blue-500/20'
                        }`}>
                          <div className="flex items-center gap-2">
                            <span className="text-xl">⏱️</span>
                            <span className={timer.urgent ? 'text-red-400' : 'text-blue-400'}>
                              {timer.expired ? 'Auto-processing...' : 'Manual review window'}
                            </span>
                          </div>
                          <div className={`text-2xl font-mono font-bold ${
                            timer.expired ? 'text-yellow-400' : timer.urgent ? 'text-red-400' : 'text-blue-400'
                          }`}>
                            {timer.text}
                          </div>
                        </div>
                      )}
                      
                      <div className="flex flex-col lg:flex-row gap-4">
                        {/* Offer Info */}
                        <div className="flex-1">
                          <div className="flex items-start gap-3 mb-4">
                            <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center text-xl">
                              📨
                            </div>
                            <div>
                              <h3 className="font-semibold">{offer.product_name}</h3>
                              <div className="text-sm text-gray-400">
                                {offer.product_quantity} × {offer.quantity}
                              </div>
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-xs px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded-full">
                                  🌐 {offer.platform_name || offer.platform}
                                </span>
                              </div>
                              <div className="text-xs text-gray-500 mt-1">
                                From: {offer.buyer_name} • {offer.city || offer.pincode}
                              </div>
                            </div>
                          </div>

                          {offer.message && (
                            <div className="bg-white/5 rounded-lg p-3 mb-4">
                              <div className="text-xs text-gray-500 mb-1">Buyer&apos;s Message:</div>
                              <p className="text-sm">&quot;{offer.message}&quot;</p>
                            </div>
                          )}

                          <div className="grid grid-cols-3 gap-4">
                            <div>
                              <div className="text-xs text-gray-500">Your Price</div>
                              <div className="text-lg font-bold">₹{offer.original_price}</div>
                            </div>
                            <div>
                              <div className="text-xs text-gray-500">Buyer Offers</div>
                              <div className="text-lg font-bold text-green-400">₹{offer.offered_price}</div>
                            </div>
                            <div>
                              <div className="text-xs text-gray-500">Discount Asked</div>
                              <div className={`text-lg font-bold ${
                                offer.discount_percent <= autoAcceptDiscount ? 'text-green-400' :
                                offer.discount_percent > autoRejectDiscount ? 'text-red-400' : 'text-yellow-400'
                              }`}>{offer.discount_percent.toFixed(1)}%</div>
                            </div>
                          </div>
                          
                          {/* Auto-action preview */}
                          {!manualReviewOnly && (
                            <div className="mt-3 text-xs text-gray-500">
                              {offer.discount_percent <= autoAcceptDiscount && (
                                <span className="text-green-400">✓ Will auto-accept if no response</span>
                              )}
                              {offer.discount_percent > autoRejectDiscount && (
                                <span className="text-red-400">✗ Will auto-reject if no response</span>
                              )}
                              {offer.discount_percent > autoAcceptDiscount && offer.discount_percent <= autoRejectDiscount && (
                                <span className="text-blue-400">↔ Will auto-counter at {autoAcceptDiscount}% if no response</span>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Actions */}
                        <div className="flex flex-col gap-2 lg:w-48">
                          <button
                            onClick={() => handleRespond(offer.offer_id, 'accept')}
                            className="w-full py-3 bg-green-500 hover:bg-green-600 rounded-lg font-medium"
                          >
                            ✓ Accept ₹{offer.offered_price}
                          </button>
                          <button
                            onClick={() => setRespondingOffer(offer)}
                            className="w-full py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium"
                          >
                            💬 Counter Offer
                          </button>
                          <button
                            onClick={() => handleRespond(offer.offer_id, 'reject')}
                            className="w-full py-3 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg font-medium"
                          >
                            ✗ Reject
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}

                {pendingOffers.length === 0 && (
                  <div className="glass rounded-xl p-12 text-center">
                    <div className="text-4xl mb-4">🎉</div>
                    <h3 className="text-xl font-bold mb-2">All Caught Up!</h3>
                    <p className="text-gray-400">No pending offers to review</p>
                  </div>
                )}
              </div>
            )}

            {/* Deals Tab */}
            {activeTab === 'deals' && (
              <div className="space-y-4">
                {deals.map((deal) => (
                  <div key={deal.deal_id} className="glass rounded-xl p-5">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex items-start gap-3">
                        <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center text-xl">
                          💰
                        </div>
                        <div>
                          <h3 className="font-semibold">{deal.product_name}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded-full">
                              🌐 {deal.platform_name || deal.platform}
                            </span>
                          </div>
                          <div className="text-sm text-gray-400 mt-1">Buyer: {deal.buyer_name}</div>
                          <div className="text-xs text-gray-500 mt-1">{formatDate(deal.created_at)}</div>
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-6">
                        <div className="text-center">
                          <div className="text-xs text-gray-500">Listed Price</div>
                          <div className="text-gray-400">₹{deal.original_price}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-gray-500">Sold At</div>
                          <div className="text-green-400 font-bold">₹{deal.final_price}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-xs text-gray-500">Revenue</div>
                          <div className="text-emerald-400 font-bold">₹{deal.total_amount}</div>
                        </div>
                      </div>

                      <span className="px-3 py-1 bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg text-sm">
                        {deal.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                  </div>
                ))}

                {deals.length === 0 && (
                  <div className="glass rounded-xl p-12 text-center">
                    <div className="text-4xl mb-4">📈</div>
                    <h3 className="text-xl font-bold mb-2">No Deals Yet</h3>
                    <p className="text-gray-400">Accept offers to start making deals!</p>
                  </div>
                )}
              </div>
            )}

            {/* Settings Tab */}
            {activeTab === 'settings' && (
              <div className="glass rounded-xl p-6 max-w-2xl">
                <h2 className="font-bold text-lg mb-6">⚙️ Seller Settings</h2>
                
                <div className="space-y-6">
                  {/* Manual Review Only Toggle */}
                  <div className="p-4 bg-white/5 rounded-xl">
                    <div className="flex items-center justify-between">
                      <div>
                        <label className="font-medium">Manual Review Only</label>
                        <p className="text-xs text-gray-500 mt-1">
                          When ON, offers never auto-process (you must always respond manually)
                        </p>
                      </div>
                      <button
                        onClick={() => setManualReviewOnly(!manualReviewOnly)}
                        className={`relative w-14 h-7 rounded-full transition-colors ${
                          manualReviewOnly ? 'bg-emerald-500' : 'bg-gray-600'
                        }`}
                      >
                        <div
                          className={`absolute top-1 w-5 h-5 bg-white rounded-full transition-transform ${
                            manualReviewOnly ? 'left-8' : 'left-1'
                          }`}
                        />
                      </button>
                    </div>
                  </div>

                  {/* Hybrid Mode Settings (shown when manual review only is OFF) */}
                  {!manualReviewOnly && (
                    <div className="p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl">
                      <div className="flex items-center gap-2 mb-4">
                        <span>⚡</span>
                        <span className="font-medium text-blue-400">Hybrid Mode (Manual + Auto)</span>
                      </div>
                      
                      <div className="bg-white/5 rounded-lg p-3 mb-4 text-sm">
                        <p className="text-gray-300">
                          📋 <strong>How it works:</strong>
                        </p>
                        <ol className="text-gray-400 text-xs mt-2 space-y-1 list-decimal list-inside">
                          <li>You get <span className="text-blue-400 font-bold">{manualReviewTimeout} minutes</span> to manually respond</li>
                          <li>If discount ≤ <span className="text-green-400 font-bold">{autoAcceptDiscount}%</span> → Auto-Accept</li>
                          <li>If discount &gt; <span className="text-red-400 font-bold">{autoRejectDiscount}%</span> → Auto-Reject</li>
                          <li>Otherwise → Auto-Counter at {autoAcceptDiscount}% discount</li>
                        </ol>
                      </div>

                      {/* Manual Review Timeout */}
                      <div className="mb-4">
                        <label className="block text-sm text-gray-400 mb-2">
                          Manual Review Window (minutes)
                        </label>
                        <div className="flex items-center gap-4">
                          <input
                            type="range"
                            min="1"
                            max="30"
                            value={manualReviewTimeout}
                            onChange={(e) => setManualReviewTimeout(Number(e.target.value))}
                            className="flex-1"
                          />
                          <span className="w-16 text-center font-bold text-blue-400">{manualReviewTimeout} min</span>
                        </div>
                      </div>
                      
                      {/* Auto-Accept Threshold */}
                      <div className="mb-4">
                        <label className="block text-sm text-gray-400 mb-2">
                          Auto-Accept if discount ≤
                        </label>
                        <div className="flex items-center gap-4">
                          <input
                            type="range"
                            min="0"
                            max="25"
                            value={autoAcceptDiscount}
                            onChange={(e) => setAutoAcceptDiscount(Number(e.target.value))}
                            className="flex-1"
                          />
                          <span className="w-12 text-center font-bold text-green-400">{autoAcceptDiscount}%</span>
                        </div>
                      </div>
                      
                      {/* Auto-Reject Threshold */}
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">
                          Auto-Reject if discount &gt;
                        </label>
                        <div className="flex items-center gap-4">
                          <input
                            type="range"
                            min="15"
                            max="50"
                            value={autoRejectDiscount}
                            onChange={(e) => setAutoRejectDiscount(Number(e.target.value))}
                            className="flex-1"
                          />
                          <span className="w-12 text-center font-bold text-red-400">{autoRejectDiscount}%</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {manualReviewOnly && (
                    <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                      <div className="flex items-center gap-2 text-emerald-400">
                        <span>✋</span>
                        <span className="font-medium">100% Manual Mode Active</span>
                      </div>
                      <p className="text-xs text-gray-400 mt-2">
                        All offers will wait for your manual response. No automatic processing.
                      </p>
                    </div>
                  )}

                  <button
                    onClick={handleUpdateSettings}
                    className="w-full py-3 bg-emerald-500 hover:bg-emerald-600 rounded-lg font-medium"
                  >
                    Save Settings
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Counter Offer Modal */}
      {respondingOffer && (
        <div 
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setRespondingOffer(null)}
        >
          <div 
            className="glass rounded-2xl p-6 max-w-md w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="font-bold text-lg mb-4">💬 Make Counter Offer</h3>
            
            <div className="bg-white/5 rounded-lg p-4 mb-4">
              <div className="font-medium mb-1">{respondingOffer.product_name}</div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded-full">
                  🌐 {respondingOffer.platform_name || respondingOffer.platform}
                </span>
                <span className="text-xs text-gray-500">from {respondingOffer.buyer_name}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Your Price:</span>
                  <span className="ml-2">₹{respondingOffer.original_price}</span>
                </div>
                <div>
                  <span className="text-gray-500">Buyer Offers:</span>
                  <span className="ml-2 text-green-400">₹{respondingOffer.offered_price}</span>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2">Your Counter Price</label>
              <input
                type="number"
                value={counterPrice}
                onChange={(e) => setCounterPrice(e.target.value)}
                placeholder={`Between ₹${respondingOffer.offered_price} and ₹${respondingOffer.original_price}`}
                className="w-full bg-white/10 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm text-gray-400 mb-2">Message (optional)</label>
              <textarea
                value={counterMessage}
                onChange={(e) => setCounterMessage(e.target.value)}
                placeholder="e.g., This is my best price..."
                rows={2}
                className="w-full bg-white/10 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setRespondingOffer(null)}
                className="flex-1 py-3 bg-white/10 hover:bg-white/20 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={() => handleRespond(respondingOffer.offer_id, 'counter')}
                disabled={!counterPrice || parseFloat(counterPrice) <= respondingOffer.offered_price || parseFloat(counterPrice) >= respondingOffer.original_price}
                className="flex-1 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 rounded-lg font-medium"
              >
                Send Counter
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

