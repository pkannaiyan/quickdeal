'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

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
  created_at: string;
}

interface Offer {
  offer_id: string;
  product_name: string;
  buyer_name: string;
  platform: string;
  platform_name: string;
  original_price: number;
  offered_price: number;
  discount_percent: number;
  status: string;
  created_at: string;
}

interface Deal {
  deal_id: string;
  product_name: string;
  buyer_name: string;
  platform: string;
  final_price: number;
  savings_percent: number;
  status: string;
  created_at: string;
}

interface PlatformStats {
  platform: string;
  platform_name: string;
  seller_name: string;
  total_offers: number;
  pending_offers: number;
  acceptance_rate: number;
  total_deals: number;
  total_revenue: number;
  avg_discount: number;
}

const PLATFORMS = [
  { id: 'blinkit', name: 'Blinkit', userId: 'user_blinkit' },
  { id: 'zepto', name: 'Zepto', userId: 'user_zepto' },
  { id: 'jiomart', name: 'JioMart', userId: 'user_jiomart' },
  { id: 'bigbasket', name: 'BigBasket', userId: 'user_bigbasket' },
  { id: 'instamart', name: 'Swiggy Instamart', userId: 'user_instamart' },
];

export default function AdminDashboard() {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'pending' | 'offers' | 'deals' | 'sellers'>('overview');
  const [loading, setLoading] = useState(true);
  
  // Data
  const [platformStats, setPlatformStats] = useState<PlatformStats[]>([]);
  const [recentDeals, setRecentDeals] = useState<Deal[]>([]);
  const [allOffers, setAllOffers] = useState<Offer[]>([]);
  const [allPendingOffers, setAllPendingOffers] = useState<PendingOffer[]>([]);
  const [summary, setSummary] = useState({
    totalOffers: 0,
    pendingOffers: 0,
    acceptedOffers: 0,
    rejectedOffers: 0,
    totalDeals: 0,
    totalRevenue: 0,
    avgDiscount: 0
  });

  // Response modal state
  const [respondingOffer, setRespondingOffer] = useState<PendingOffer | null>(null);
  const [counterPrice, setCounterPrice] = useState('');
  const [counterMessage, setCounterMessage] = useState('');
  const [responding, setResponding] = useState(false);

  // Check authorization
  useEffect(() => {
    const role = localStorage.getItem('userRole');
    const userId = localStorage.getItem('userId');
    
    if (role !== 'admin' || userId !== 'admin') {
      router.push('/login');
      return;
    }
    
    setIsAuthorized(true);
  }, [router]);

  // Fetch data
  useEffect(() => {
    if (isAuthorized) {
      fetchAllData();
      
      // Auto refresh every 5 seconds
      const interval = setInterval(fetchAllData, 5000);
      return () => clearInterval(interval);
    }
  }, [isAuthorized]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      // Fetch platform stats
      const statsRes = await fetch(`${API_URL}/api/negotiate/platforms/stats`);
      if (statsRes.ok) {
        const data = await statsRes.json();
        setPlatformStats(data.platforms || []);
        
        // Calculate summary
        const platforms = data.platforms || [];
        const totalOffers = platforms.reduce((sum: number, p: PlatformStats) => sum + p.total_offers, 0);
        const pendingOffers = platforms.reduce((sum: number, p: PlatformStats) => sum + p.pending_offers, 0);
        const totalDeals = platforms.reduce((sum: number, p: PlatformStats) => sum + p.total_deals, 0);
        const totalRevenue = platforms.reduce((sum: number, p: PlatformStats) => sum + p.total_revenue, 0);
        const avgDiscount = platforms.length > 0 
          ? platforms.reduce((sum: number, p: PlatformStats) => sum + p.avg_discount, 0) / platforms.length
          : 0;
        
        setSummary({
          totalOffers,
          pendingOffers,
          acceptedOffers: totalDeals,
          rejectedOffers: totalOffers - pendingOffers - totalDeals,
          totalDeals,
          totalRevenue,
          avgDiscount
        });
      }

      // Fetch recent deals
      const dealsRes = await fetch(`${API_URL}/api/negotiate/deals/recent?limit=20`);
      if (dealsRes.ok) {
        const data = await dealsRes.json();
        setRecentDeals(data.deals || []);
      }

      // Fetch all offers using admin endpoint
      const allOffersRes = await fetch(`${API_URL}/api/negotiate/admin/all-offers?limit=100`);
      if (allOffersRes.ok) {
        const data = await allOffersRes.json();
        setAllOffers(data.offers || []);
      }

      // Fetch all pending offers from all platforms
      const pendingPromises = PLATFORMS.map(async (platform) => {
        try {
          const res = await fetch(`${API_URL}/api/negotiate/seller/pending`, {
            headers: { 'X-User-Id': platform.userId }
          });
          if (res.ok) {
            const data = await res.json();
            return (data.pending_offers || []).map((o: PendingOffer) => ({
              ...o,
              platform: platform.id,
              platform_name: platform.name
            }));
          }
        } catch {}
        return [];
      });
      
      const pendingResults = await Promise.all(pendingPromises);
      const allPending = pendingResults.flat();
      allPending.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setAllPendingOffers(allPending);

    } catch (e) {
      console.error('Fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = async (offer: PendingOffer, action: 'accept' | 'reject' | 'counter') => {
    if (action === 'counter') {
      setRespondingOffer(offer);
      return;
    }

    setResponding(true);
    try {
      const platform = PLATFORMS.find(p => p.id === offer.platform);
      if (!platform) return;

      const response = await fetch(`${API_URL}/api/negotiate/seller/offers/${offer.offer_id}/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': platform.userId
        },
        body: JSON.stringify({ action })
      });

      if (response.ok) {
        fetchAllData();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to respond');
      }
    } catch (e) {
      console.error('Response error:', e);
      alert('Network error');
    } finally {
      setResponding(false);
    }
  };

  const handleSubmitCounter = async () => {
    if (!respondingOffer || !counterPrice) return;

    setResponding(true);
    try {
      const platform = PLATFORMS.find(p => p.id === respondingOffer.platform);
      if (!platform) return;

      const response = await fetch(`${API_URL}/api/negotiate/seller/offers/${respondingOffer.offer_id}/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': platform.userId
        },
        body: JSON.stringify({
          action: 'counter',
          counter_price: parseFloat(counterPrice),
          message: counterMessage || undefined
        })
      });

      if (response.ok) {
        setRespondingOffer(null);
        setCounterPrice('');
        setCounterMessage('');
        fetchAllData();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to send counter');
      }
    } catch (e) {
      console.error('Counter error:', e);
      alert('Network error');
    } finally {
      setResponding(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userName');
    localStorage.removeItem('userEmail');
    router.push('/login');
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

  if (!isAuthorized) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900/10 to-slate-900">
      {/* Header */}
      <header className="glass border-b border-white/10 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-gray-400 hover:text-white">
              ← Home
            </Link>
            <div>
              <h1 className="text-2xl font-bold">
                <span className="bg-gradient-to-r from-[#00D9A5] to-[#00B894] bg-clip-text text-transparent">QuickDeal</span>
                <span className="text-white ml-2">| Admin</span>
              </h1>
              <p className="text-gray-400 text-sm">System overview & management</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {allPendingOffers.length > 0 && (
              <div className="px-3 py-1 bg-yellow-500/20 border border-yellow-500/30 rounded-full text-yellow-400 text-sm animate-pulse">
                {allPendingOffers.length} Pending
              </div>
            )}
            <div className="px-3 py-1 bg-red-500/20 border border-red-500/30 rounded-full text-red-400 text-sm">
              Admin Access
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8">
          <div className="glass rounded-xl p-4">
            <div className="text-3xl font-bold text-red-400">{summary.totalOffers}</div>
            <div className="text-sm text-gray-400">Total Offers</div>
          </div>
          <div className="glass rounded-xl p-4 cursor-pointer hover:bg-white/5" onClick={() => setActiveTab('pending')}>
            <div className="text-3xl font-bold text-yellow-400">{allPendingOffers.length}</div>
            <div className="text-sm text-gray-400">Pending ⚡</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="text-3xl font-bold text-green-400">{summary.acceptedOffers}</div>
            <div className="text-sm text-gray-400">Accepted</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="text-3xl font-bold text-red-400">{summary.rejectedOffers}</div>
            <div className="text-sm text-gray-400">Rejected</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="text-3xl font-bold text-blue-400">{summary.totalDeals}</div>
            <div className="text-sm text-gray-400">Deals</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="text-3xl font-bold text-emerald-400">₹{summary.totalRevenue.toFixed(0)}</div>
            <div className="text-sm text-gray-400">Revenue</div>
          </div>
          <div className="glass rounded-xl p-4">
            <div className="text-3xl font-bold text-purple-400">{summary.avgDiscount.toFixed(1)}%</div>
            <div className="text-sm text-gray-400">Avg Discount</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {(['overview', 'pending', 'offers', 'deals', 'sellers'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                activeTab === tab
                  ? 'bg-red-500 text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              {tab === 'overview' && '📊 '}
              {tab === 'pending' && '⏳ '}
              {tab === 'offers' && '📝 '}
              {tab === 'deals' && '✅ '}
              {tab === 'sellers' && '🏪 '}
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {tab === 'pending' && allPendingOffers.length > 0 && (
                <span className="ml-2 bg-yellow-500 text-black text-xs px-2 py-0.5 rounded-full">
                  {allPendingOffers.length}
                </span>
              )}
            </button>
          ))}
        </div>

        {loading && activeTab === 'overview' ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full" />
          </div>
        ) : (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="grid md:grid-cols-2 gap-6">
                {/* Pending Offers Quick View */}
                <div className="glass rounded-xl p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="font-bold text-lg flex items-center gap-2">
                      ⏳ Pending Offers
                      {allPendingOffers.length > 0 && (
                        <span className="bg-yellow-500/20 text-yellow-400 text-xs px-2 py-0.5 rounded-full animate-pulse">
                          Action Required
                        </span>
                      )}
                    </h2>
                    <button
                      onClick={() => setActiveTab('pending')}
                      className="text-sm text-yellow-400 hover:text-yellow-300"
                    >
                      View All →
                    </button>
                  </div>
                  <div className="space-y-3">
                    {allPendingOffers.slice(0, 3).map((offer) => (
                      <div key={offer.offer_id} className="bg-white/5 rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <div className="font-medium text-sm">{offer.product_name}</div>
                            <div className="text-xs text-gray-500">{offer.buyer_name}</div>
                            <span className="text-[10px] px-1.5 py-0.5 bg-indigo-500/20 text-indigo-400 rounded mt-1 inline-block">
                              🌐 {offer.platform_name}
                            </span>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-green-400">₹{offer.offered_price}</div>
                            <div className="text-xs text-red-400">-{offer.discount_percent.toFixed(0)}%</div>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleRespond(offer, 'accept')}
                            disabled={responding}
                            className="flex-1 py-1.5 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded text-xs font-medium"
                          >
                            ✓ Accept
                          </button>
                          <button
                            onClick={() => handleRespond(offer, 'counter')}
                            disabled={responding}
                            className="flex-1 py-1.5 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded text-xs font-medium"
                          >
                            ↔ Counter
                          </button>
                          <button
                            onClick={() => handleRespond(offer, 'reject')}
                            disabled={responding}
                            className="flex-1 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded text-xs font-medium"
                          >
                            ✗ Reject
                          </button>
                        </div>
                      </div>
                    ))}
                    {allPendingOffers.length === 0 && (
                      <p className="text-gray-500 text-center py-8">No pending offers</p>
                    )}
                  </div>
                </div>

                {/* Platform Performance */}
                <div className="glass rounded-xl p-6">
                  <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
                    🏪 Platform Performance
                  </h2>
                  <div className="space-y-3">
                    {platformStats.map((platform) => (
                      <div key={platform.platform} className="bg-white/5 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <div className="font-medium">{platform.platform_name}</div>
                            <div className="text-xs text-gray-500">{platform.seller_name}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-emerald-400">₹{platform.total_revenue.toFixed(0)}</div>
                            <div className="text-xs text-gray-500">{platform.total_deals} deals</div>
                          </div>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">{platform.total_offers} offers</span>
                          <span className="text-yellow-400">{platform.pending_offers} pending</span>
                          <span className="text-green-400">{platform.acceptance_rate.toFixed(0)}% accept</span>
                        </div>
                      </div>
                    ))}
                    {platformStats.length === 0 && (
                      <p className="text-gray-500 text-center py-8">No platform data yet</p>
                    )}
                  </div>
                </div>

                {/* Recent Deals */}
                <div className="glass rounded-xl p-6">
                  <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
                    ✅ Recent Deals
                  </h2>
                  <div className="space-y-3">
                    {recentDeals.slice(0, 5).map((deal) => (
                      <div key={deal.deal_id} className="bg-white/5 rounded-lg p-3">
                        <div className="flex justify-between items-start mb-1">
                          <div className="font-medium text-sm line-clamp-1">{deal.product_name}</div>
                          <span className="text-green-400 font-bold">₹{deal.final_price}</span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>{deal.buyer_name} → {deal.platform}</span>
                          <span>{deal.savings_percent.toFixed(0)}% off</span>
                        </div>
                      </div>
                    ))}
                    {recentDeals.length === 0 && (
                      <p className="text-gray-500 text-center py-8">No deals yet</p>
                    )}
                  </div>
                </div>

                {/* Quick Links */}
                <div className="glass rounded-xl p-6">
                  <h2 className="font-bold text-lg mb-4">🔗 Quick Actions</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <Link
                      href="/buyer"
                      className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-xl text-center hover:bg-purple-500/20 transition-all"
                    >
                      <div className="text-2xl mb-2">🛒</div>
                      <div className="font-medium text-purple-400">Buyer View</div>
                    </Link>
                    <Link
                      href="/seller"
                      className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-center hover:bg-emerald-500/20 transition-all"
                    >
                      <div className="text-2xl mb-2">🏪</div>
                      <div className="font-medium text-emerald-400">Seller View</div>
                    </Link>
                    <Link
                      href="/dashboard"
                      className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl text-center hover:bg-blue-500/20 transition-all"
                    >
                      <div className="text-2xl mb-2">📊</div>
                      <div className="font-medium text-blue-400">Analytics</div>
                    </Link>
                    <Link
                      href="/"
                      className="p-4 bg-orange-500/10 border border-orange-500/20 rounded-xl text-center hover:bg-orange-500/20 transition-all"
                    >
                      <div className="text-2xl mb-2">🔍</div>
                      <div className="font-medium text-orange-400">Search App</div>
                    </Link>
                  </div>
                </div>
              </div>
            )}

            {/* Pending Offers Tab - NEW */}
            {activeTab === 'pending' && (
              <div className="space-y-4">
                <div className="glass rounded-xl p-4 border-l-4 border-yellow-500">
                  <p className="text-yellow-400 font-medium">
                    ⚡ Admin can accept, reject, or counter offers on behalf of any seller
                  </p>
                </div>
                
                {allPendingOffers.length === 0 ? (
                  <div className="glass rounded-xl p-12 text-center">
                    <div className="text-4xl mb-4">✅</div>
                    <h3 className="text-xl font-bold mb-2">All Caught Up!</h3>
                    <p className="text-gray-400">No pending offers to review</p>
                  </div>
                ) : (
                  allPendingOffers.map((offer) => (
                    <div key={offer.offer_id} className="glass rounded-xl p-5">
                      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-start gap-3 mb-3">
                            <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center text-xl">
                              🛍️
                            </div>
                            <div>
                              <h3 className="font-semibold">{offer.product_name}</h3>
                              <div className="text-sm text-gray-400">
                                {offer.product_quantity} × {offer.quantity}
                              </div>
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-xs px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded-full">
                                  🌐 {offer.platform_name}
                                </span>
                                <span className="text-xs text-gray-500">
                                  Buyer: {offer.buyer_name}
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="grid grid-cols-3 gap-4 mb-3">
                            <div>
                              <div className="text-xs text-gray-500">Original Price</div>
                              <div className="font-bold">₹{offer.original_price}</div>
                            </div>
                            <div>
                              <div className="text-xs text-gray-500">Offered Price</div>
                              <div className="font-bold text-green-400">₹{offer.offered_price}</div>
                            </div>
                            <div>
                              <div className="text-xs text-gray-500">Discount</div>
                              <div className="font-bold text-yellow-400">-{offer.discount_percent.toFixed(1)}%</div>
                            </div>
                          </div>

                          {offer.message && (
                            <div className="p-2 bg-white/5 rounded-lg text-sm text-gray-400">
                              💬 "{offer.message}"
                            </div>
                          )}
                        </div>

                        <div className="flex flex-col gap-2 lg:w-48">
                          <button
                            onClick={() => handleRespond(offer, 'accept')}
                            disabled={responding}
                            className="w-full py-3 bg-green-500 hover:bg-green-600 disabled:bg-gray-600 rounded-lg font-medium"
                          >
                            ✓ Accept ₹{offer.offered_price}
                          </button>
                          <button
                            onClick={() => handleRespond(offer, 'counter')}
                            disabled={responding}
                            className="w-full py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 rounded-lg font-medium"
                          >
                            ↔ Counter Offer
                          </button>
                          <button
                            onClick={() => handleRespond(offer, 'reject')}
                            disabled={responding}
                            className="w-full py-3 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg font-medium"
                          >
                            ✗ Reject
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* All Offers Tab */}
            {activeTab === 'offers' && (
              <div className="glass rounded-xl overflow-hidden">
                <div className="p-4 border-b border-white/10">
                  <h2 className="font-bold text-lg">📝 All Offers ({allOffers.length})</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-white/5">
                      <tr>
                        <th className="text-left p-3 text-sm text-gray-400">Product</th>
                        <th className="text-left p-3 text-sm text-gray-400">Buyer</th>
                        <th className="text-left p-3 text-sm text-gray-400">Platform</th>
                        <th className="text-right p-3 text-sm text-gray-400">Original</th>
                        <th className="text-right p-3 text-sm text-gray-400">Offered</th>
                        <th className="text-right p-3 text-sm text-gray-400">Discount</th>
                        <th className="text-center p-3 text-sm text-gray-400">Status</th>
                        <th className="text-right p-3 text-sm text-gray-400">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {allOffers.map((offer) => (
                        <tr key={offer.offer_id} className="border-t border-white/5 hover:bg-white/5">
                          <td className="p-3 text-sm max-w-[200px] truncate">{offer.product_name}</td>
                          <td className="p-3 text-sm text-gray-400">{offer.buyer_name}</td>
                          <td className="p-3 text-sm text-gray-400">{offer.platform_name}</td>
                          <td className="p-3 text-sm text-right">₹{offer.original_price}</td>
                          <td className="p-3 text-sm text-right text-green-400">₹{offer.offered_price}</td>
                          <td className="p-3 text-sm text-right text-yellow-400">{offer.discount_percent.toFixed(1)}%</td>
                          <td className="p-3">
                            <span className={`px-2 py-0.5 rounded border text-xs ${getStatusColor(offer.status)}`}>
                              {offer.status}
                            </span>
                          </td>
                          <td className="p-3 text-sm text-right text-gray-500">{formatDate(offer.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {allOffers.length === 0 && (
                    <div className="text-center py-12 text-gray-500">No offers found</div>
                  )}
                </div>
              </div>
            )}

            {/* Deals Tab */}
            {activeTab === 'deals' && (
              <div className="glass rounded-xl overflow-hidden">
                <div className="p-4 border-b border-white/10">
                  <h2 className="font-bold text-lg">✅ All Deals ({recentDeals.length})</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-white/5">
                      <tr>
                        <th className="text-left p-3 text-sm text-gray-400">Product</th>
                        <th className="text-left p-3 text-sm text-gray-400">Buyer</th>
                        <th className="text-left p-3 text-sm text-gray-400">Platform</th>
                        <th className="text-right p-3 text-sm text-gray-400">Price</th>
                        <th className="text-right p-3 text-sm text-gray-400">Discount</th>
                        <th className="text-center p-3 text-sm text-gray-400">Status</th>
                        <th className="text-right p-3 text-sm text-gray-400">Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentDeals.map((deal) => (
                        <tr key={deal.deal_id} className="border-t border-white/5 hover:bg-white/5">
                          <td className="p-3 text-sm max-w-[200px] truncate">{deal.product_name}</td>
                          <td className="p-3 text-sm text-gray-400">{deal.buyer_name}</td>
                          <td className="p-3 text-sm text-gray-400">{deal.platform}</td>
                          <td className="p-3 text-sm text-right text-green-400">₹{deal.final_price}</td>
                          <td className="p-3 text-sm text-right text-emerald-400">{deal.savings_percent.toFixed(1)}%</td>
                          <td className="p-3">
                            <span className={`px-2 py-0.5 rounded border text-xs ${getStatusColor(deal.status)}`}>
                              {deal.status}
                            </span>
                          </td>
                          <td className="p-3 text-sm text-right text-gray-500">{formatDate(deal.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {recentDeals.length === 0 && (
                    <div className="text-center py-12 text-gray-500">No deals found</div>
                  )}
                </div>
              </div>
            )}

            {/* Sellers Tab */}
            {activeTab === 'sellers' && (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {platformStats.map((platform) => (
                  <div key={platform.platform} className="glass rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center text-2xl">
                        🏪
                      </div>
                      <div>
                        <h3 className="font-bold">{platform.platform_name}</h3>
                        <p className="text-sm text-gray-400">{platform.seller_name}</p>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="bg-white/5 rounded-lg p-2">
                        <div className="text-xl font-bold text-blue-400">{platform.total_offers}</div>
                        <div className="text-gray-500">Total Offers</div>
                      </div>
                      <div className="bg-white/5 rounded-lg p-2">
                        <div className="text-xl font-bold text-yellow-400">{platform.pending_offers}</div>
                        <div className="text-gray-500">Pending</div>
                      </div>
                      <div className="bg-white/5 rounded-lg p-2">
                        <div className="text-xl font-bold text-green-400">{platform.acceptance_rate.toFixed(0)}%</div>
                        <div className="text-gray-500">Accept Rate</div>
                      </div>
                      <div className="bg-white/5 rounded-lg p-2">
                        <div className="text-xl font-bold text-emerald-400">₹{platform.total_revenue.toFixed(0)}</div>
                        <div className="text-gray-500">Revenue</div>
                      </div>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-white/10 flex justify-between text-sm">
                      <span className="text-gray-400">{platform.total_deals} deals</span>
                      <span className="text-purple-400">{platform.avg_discount.toFixed(1)}% avg discount</span>
                    </div>
                  </div>
                ))}
                
                {platformStats.length === 0 && (
                  <div className="col-span-full glass rounded-xl p-12 text-center">
                    <div className="text-4xl mb-4">🏪</div>
                    <h3 className="text-xl font-bold mb-2">No Seller Data</h3>
                    <p className="text-gray-400">Seller statistics will appear here once offers are made</p>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>

      {/* Counter Offer Modal */}
      {respondingOffer && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="glass rounded-2xl p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">↔ Counter Offer</h2>
            
            <div className="bg-white/5 rounded-lg p-4 mb-4">
              <div className="font-medium mb-1">{respondingOffer.product_name}</div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs px-2 py-0.5 bg-indigo-500/20 text-indigo-400 rounded-full">
                  🌐 {respondingOffer.platform_name}
                </span>
                <span className="text-xs text-gray-500">Buyer: {respondingOffer.buyer_name}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Original:</span>
                  <span className="ml-2">₹{respondingOffer.original_price}</span>
                </div>
                <div>
                  <span className="text-gray-500">Offered:</span>
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
                placeholder="Add a message for the buyer..."
                rows={2}
                className="w-full bg-white/10 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setRespondingOffer(null);
                  setCounterPrice('');
                  setCounterMessage('');
                }}
                className="flex-1 py-3 bg-white/10 hover:bg-white/20 rounded-lg font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitCounter}
                disabled={!counterPrice || parseFloat(counterPrice) <= respondingOffer.offered_price || parseFloat(counterPrice) >= respondingOffer.original_price || responding}
                className="flex-1 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 rounded-lg font-medium"
              >
                {responding ? 'Sending...' : 'Send Counter'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
