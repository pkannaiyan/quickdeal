'use client';

import { useState, useEffect, useCallback } from 'react';

interface Deal {
  product_id: string;
  product_name: string;
  brand: string | null;
  category: string;
  quantity: string;
  image_url?: string;
  best_price: number;
  highest_price: number;
  savings_amount: number;
  savings_percent: number;
  best_platform: string;
  best_platform_name: string;
  best_platform_logo: string;
  best_delivery_time: string;
  available_on: number;
  deal_score: number;
}

interface DealsResponse {
  total_deals: number;
  deals: Deal[];
}

interface DealsSectionProps {
  apiUrl: string;
  onOneClickCheckout?: (deal: Deal) => void;
}

const PLATFORM_COLORS: Record<string, { bg: string; text: string }> = {
  'blinkit': { bg: 'from-yellow-400 to-yellow-500', text: 'text-black' },
  'zepto': { bg: 'from-purple-500 to-purple-600', text: 'text-white' },
  'instamart': { bg: 'from-orange-500 to-orange-600', text: 'text-white' },
  'bigbasket': { bg: 'from-lime-500 to-lime-600', text: 'text-black' },
  'jiomart': { bg: 'from-blue-500 to-blue-600', text: 'text-white' },
};

const REFRESH_INTERVAL = 5 * 60 * 1000;

export default function DealsSection({ apiUrl, onOneClickCheckout }: DealsSectionProps) {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [timeUntilRefresh, setTimeUntilRefresh] = useState(REFRESH_INTERVAL / 1000);

  const fetchDeals = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      
      const timestamp = Date.now();
      const response = await fetch(`${apiUrl}/api/search/deals?min_savings=5&limit=6&_t=${timestamp}`);
      if (!response.ok) throw new Error('Failed to fetch deals');
      const data: DealsResponse = await response.json();
      setDeals(data.deals);
      setLastUpdated(new Date());
      setTimeUntilRefresh(REFRESH_INTERVAL / 1000);
      setError(null);
    } catch (err) {
      if (!isRefresh) {
        setError('Unable to load deals');
      }
      console.error('Deals fetch error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [apiUrl]);

  useEffect(() => {
    fetchDeals();
  }, [fetchDeals]);

  useEffect(() => {
    const refreshInterval = setInterval(() => fetchDeals(true), REFRESH_INTERVAL);
    return () => clearInterval(refreshInterval);
  }, [fetchDeals]);

  useEffect(() => {
    const countdownInterval = setInterval(() => {
      setTimeUntilRefresh((prev) => prev <= 1 ? REFRESH_INTERVAL / 1000 : prev - 1);
    }, 1000);
    return () => clearInterval(countdownInterval);
  }, []);

  const formatTimeRemaining = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <section className="mt-16">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-12 h-12 rounded-2xl gradient-coral flex items-center justify-center text-2xl">
            🔥
          </div>
          <div>
            <h2 className="text-2xl font-bold">Today&apos;s Hot Deals</h2>
            <p className="text-gray-500 text-sm">Loading fresh deals...</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass rounded-2xl p-6 h-72">
              <div className="shimmer h-32 rounded-xl mb-4" />
              <div className="shimmer h-6 w-2/3 rounded mb-3" />
              <div className="shimmer h-8 w-1/3 rounded" />
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (error || deals.length === 0) {
    return null;
  }

  return (
    <section className="mt-16">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl gradient-coral flex items-center justify-center text-3xl shadow-lg glow-coral">
            🔥
          </div>
          <div>
            <h2 className="text-2xl md:text-3xl font-bold">
              Today&apos;s <span className="gradient-text">Hot Deals</span>
            </h2>
            <p className="text-gray-500 text-sm">
              Save big on popular products • {deals.length} deals found
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Live indicator */}
          <div className="flex items-center gap-2 px-4 py-2 glass rounded-full">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00D9A5] opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00D9A5]" />
            </span>
            <span className="text-sm text-gray-400">Live</span>
          </div>
          
          {/* Refresh timer */}
          <div className="flex items-center gap-2 px-4 py-2 glass rounded-full">
            <span className="text-gray-500 text-sm">Refresh in</span>
            <span className="font-mono text-[#00D9A5] font-medium">
              {formatTimeRemaining(timeUntilRefresh)}
            </span>
          </div>
          
          {/* Manual refresh */}
          <button
            onClick={() => fetchDeals(true)}
            disabled={refreshing}
            className="p-3 glass rounded-full hover:bg-white/10 transition-all disabled:opacity-50"
          >
            <svg 
              className={`w-5 h-5 ${refreshing ? 'animate-spin text-[#00D9A5]' : 'text-gray-400'}`} 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {/* Deals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {deals.map((deal, index) => (
          <DealCard 
            key={`${deal.product_id}-${lastUpdated?.getTime()}`} 
            deal={deal} 
            rank={index + 1} 
            onOneClickCheckout={onOneClickCheckout ? () => onOneClickCheckout(deal) : undefined}
          />
        ))}
      </div>
    </section>
  );
}

function DealCard({ deal, rank, onOneClickCheckout }: { deal: Deal; rank: number; onOneClickCheckout?: () => void }) {
  const platformStyle = PLATFORM_COLORS[deal.best_platform] || { bg: 'from-gray-500 to-gray-600', text: 'text-white' };
  
  const getRankStyle = () => {
    if (rank === 1) return { badge: '🥇', bg: 'from-yellow-400 to-amber-500', label: '#1 Best Deal' };
    if (rank === 2) return { badge: '🥈', bg: 'from-gray-300 to-gray-400', label: '#2 Hot' };
    if (rank === 3) return { badge: '🥉', bg: 'from-amber-600 to-amber-700', label: '#3 Popular' };
    return null;
  };

  const getBuyUrl = () => {
    const searchTerm = encodeURIComponent(deal.product_name);
    const platformUrls: Record<string, string> = {
      'blinkit': `https://blinkit.com/s?q=${searchTerm}`,
      'zepto': `https://www.zeptonow.com/search?query=${searchTerm}`,
      'instamart': `https://www.swiggy.com/instamart/search?query=${searchTerm}`,
      'bigbasket': `https://www.bigbasket.com/ps/?q=${searchTerm}`,
      'jiomart': `https://www.jiomart.com/search?q=${searchTerm}`,
    };
    return platformUrls[deal.best_platform] || `https://www.google.com/search?q=${searchTerm}+buy+online`;
  };

  const rankStyle = getRankStyle();

  return (
    <div className={`group glass rounded-2xl overflow-hidden card-hover ${rank === 1 ? 'ring-2 ring-[#00D9A5]/50' : ''}`}>
      {/* Rank Badge */}
      {rankStyle && (
        <div className={`px-4 py-2 bg-gradient-to-r ${rankStyle.bg} flex items-center justify-center gap-2`}>
          <span className="text-lg">{rankStyle.badge}</span>
          <span className={`font-bold text-sm ${rank === 1 ? 'text-black' : 'text-white'}`}>
            {rankStyle.label}
          </span>
        </div>
      )}

      {/* Product Image & Info */}
      <div className="relative">
        <div className="h-40 bg-gradient-to-br from-gray-800/50 to-gray-900/50 flex items-center justify-center overflow-hidden">
          {deal.image_url ? (
            <img
              src={deal.image_url}
              alt={deal.product_name}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              onError={(e) => {
                (e.target as HTMLImageElement).src = `https://via.placeholder.com/200x150.png?text=${encodeURIComponent(deal.product_name.slice(0, 8))}`;
              }}
            />
          ) : (
            <div className="text-5xl opacity-50">📦</div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-[#0A0F1C] via-transparent to-transparent" />
        </div>
        
        {/* Savings Badge */}
        <div className="absolute top-3 right-3">
          <div className="gradient-mint px-3 py-1.5 rounded-full text-sm font-bold text-black shadow-lg">
            -{deal.savings_percent.toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        <h3 className="font-semibold text-lg line-clamp-2 mb-2 group-hover:text-[#00D9A5] transition-colors">
          {deal.product_name}
        </h3>
        
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
          {deal.brand && <span className="badge badge-info">{deal.brand}</span>}
          <span>{deal.quantity}</span>
        </div>

        {/* Price */}
        <div className="flex items-end gap-3 mb-4">
          <div className="text-3xl font-bold font-price text-[#00D9A5]">
            ₹{deal.best_price}
          </div>
          <div className="text-lg text-gray-500 line-through font-price pb-0.5">
            ₹{deal.highest_price}
          </div>
          <div className="badge badge-success ml-auto">
            Save ₹{deal.savings_amount.toFixed(0)}
          </div>
        </div>

        {/* Platform Info */}
        <div className={`p-3 rounded-xl bg-gradient-to-r ${platformStyle.bg} mb-4`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xl">{deal.best_platform_logo}</span>
              <div className={platformStyle.text}>
                <div className="font-semibold text-sm">{deal.best_platform_name}</div>
                <div className="text-xs opacity-80">{deal.best_delivery_time}</div>
              </div>
            </div>
            <div className={`text-xs font-bold ${platformStyle.text} opacity-80`}>
              Score: {deal.deal_score.toFixed(0)}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2">
          {onOneClickCheckout && (
            <button
              onClick={onOneClickCheckout}
              className="w-full py-3.5 btn-primary rounded-xl font-bold text-sm flex items-center justify-center gap-2"
            >
              <span>⚡</span>
              Buy Now @ ₹{deal.best_price}
            </button>
          )}
          
          <a
            href={getBuyUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-sm flex items-center justify-center gap-2 transition-all"
          >
            <span>🔗</span>
            Open in {deal.best_platform_name}
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}
