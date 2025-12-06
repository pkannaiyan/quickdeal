'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

interface DashboardData {
  searches: {
    total_searches: number;
    unique_queries: number;
    top_queries: { query: string; count: number }[];
    hourly_volume: Record<string, number>;
  };
  platforms: {
    total_comparisons: number;
    platforms: {
      platform_id: string;
      platform_name: string;
      logo: string;
      color: string;
      wins: number;
      win_percentage: number;
    }[];
    best_platform: any;
  };
  orders: {
    total_order_intents: number;
    total_value: number;
    average_order_value: number;
    top_products: { product_name: string; order_count: number; total_value: number }[];
  };
  categories: {
    total_category_searches: number;
    categories: { category_id: string; category_name: string; icon: string; percentage: number }[];
  };
  negotiations: {
    total_offers: number;
    status_breakdown: { accepted: number; rejected: number; countered: number; pending: number };
    success_rate: number;
    discount_distribution: Record<string, number>;
    platform_stats: { platform: string; total_offers: number; success_rate: number; avg_discount: number }[];
    total_savings: number;
    avg_savings_per_deal: number;
  };
  savings: {
    total_savings: number;
    total_deals: number;
    avg_savings_percent: number;
    platform_savings: { platform: string; total_savings: number; deal_count: number }[];
    daily_trend: { date: string; savings: number }[];
    top_products: { product: string; total_savings: number; deals: number }[];
  };
  conversions: {
    funnel: { searches: number; order_intents: number; negotiations_started: number; deals_completed: number };
    conversion_rates: { search_to_order: number; search_to_negotiate: number; negotiate_to_deal: number };
  };
  realtime: {
    searches_last_hour: number;
    orders_last_hour: number;
    current_users: number;
    avg_response_time_ms: number;
    platform_status: Record<string, { status: string; latency: number }>;
  };
}

export default function AnalyticsDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'negotiations' | 'platforms' | 'conversions'>('overview');
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      setRefreshing(true);
      const response = await fetch(`${API_URL}/api/analytics/dashboard`);
      if (response.ok) {
        const result = await response.json();
        setData(result);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0A0F1C] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#00D9A5] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-[#0A0F1C] flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <h2 className="text-xl font-bold mb-2">No Analytics Data Yet</h2>
          <p className="text-gray-400 mb-4">Start using the app to generate analytics</p>
          <Link href="/" className="btn-primary px-6 py-2 rounded-xl">
            Go to App
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0F1C]">
      {/* Header */}
      <header className="border-b border-white/5 sticky top-0 bg-[#0A0F1C]/90 backdrop-blur-xl z-40">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-gray-400 hover:text-white transition-colors">
              ← Back
            </Link>
            <div>
              <h1 className="text-2xl font-bold">
                <span className="bg-gradient-to-r from-[#00D9A5] to-[#00B894] bg-clip-text text-transparent">QuickDeal</span>
                <span className="text-white ml-2">| Analytics</span>
              </h1>
              <p className="text-gray-500 text-sm">Insights & performance metrics</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Live indicator */}
            <div className="flex items-center gap-2 px-3 py-1.5 glass rounded-full text-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00D9A5] opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00D9A5]" />
              </span>
              <span className="text-[#00D9A5]">{data.realtime.current_users} users online</span>
            </div>
            
            <button
              onClick={fetchData}
              disabled={refreshing}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
            >
              <svg className={`w-5 h-5 ${refreshing ? 'animate-spin text-[#00D9A5]' : 'text-gray-400'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1">
            {[
              { id: 'overview', label: '📊 Overview', icon: '📊' },
              { id: 'negotiations', label: '🤝 Negotiations', icon: '🤝' },
              { id: 'platforms', label: '🏪 Platforms', icon: '🏪' },
              { id: 'conversions', label: '📈 Conversions', icon: '📈' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-3 text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'text-[#00D9A5] border-b-2 border-[#00D9A5]'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                icon="🔍"
                label="Total Searches"
                value={data.searches.total_searches.toLocaleString()}
                subtext="Last 24 hours"
                color="purple"
              />
              <MetricCard
                icon="🤝"
                label="Negotiations"
                value={data.negotiations.total_offers.toLocaleString()}
                subtext={`${data.negotiations.success_rate}% success rate`}
                color="mint"
              />
              <MetricCard
                icon="💰"
                label="Total Savings"
                value={`₹${data.savings.total_savings.toLocaleString()}`}
                subtext={`${data.savings.total_deals} deals completed`}
                color="gold"
              />
              <MetricCard
                icon="⚡"
                label="Avg Response"
                value={`${data.realtime.avg_response_time_ms}ms`}
                subtext="API latency"
                color="blue"
              />
            </div>

            {/* Platform Performance */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="glass rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span>🏆</span> Platform Wins
                </h3>
                <div className="space-y-4">
                  {data.platforms.platforms.slice(0, 5).map((platform, index) => (
                    <div key={platform.platform_id} className="flex items-center gap-4">
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center text-lg" style={{ backgroundColor: platform.color + '20' }}>
                        {platform.logo}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between mb-1">
                          <span className="font-medium">{platform.platform_name}</span>
                          <span className="text-[#00D9A5] font-mono">{platform.win_percentage}%</span>
                        </div>
                        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                          <div 
                            className="h-full rounded-full transition-all duration-1000"
                            style={{ 
                              width: `${platform.win_percentage}%`,
                              backgroundColor: platform.color
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top Searches */}
              <div className="glass rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span>🔥</span> Top Searches
                </h3>
                <div className="space-y-3">
                  {data.searches.top_queries.slice(0, 8).map((query, index) => (
                    <div key={query.query} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs font-bold">
                          {index + 1}
                        </span>
                        <span className="capitalize">{query.query}</span>
                      </div>
                      <span className="text-gray-400 font-mono text-sm">{query.count} searches</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Category Distribution */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span>📦</span> Category Distribution
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {data.categories.categories.slice(0, 10).map((cat) => (
                  <div key={cat.category_id} className="text-center p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors">
                    <div className="text-3xl mb-2">{cat.icon}</div>
                    <div className="font-medium text-sm">{cat.category_name}</div>
                    <div className="text-[#00D9A5] font-bold">{cat.percentage}%</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Negotiations Tab */}
        {activeTab === 'negotiations' && (
          <div className="space-y-8">
            {/* Negotiation Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                icon="📩"
                label="Total Offers"
                value={data.negotiations.total_offers.toString()}
                color="purple"
              />
              <MetricCard
                icon="✅"
                label="Accepted"
                value={data.negotiations.status_breakdown.accepted.toString()}
                subtext={`${data.negotiations.success_rate}% success`}
                color="mint"
              />
              <MetricCard
                icon="❌"
                label="Rejected"
                value={data.negotiations.status_breakdown.rejected.toString()}
                color="coral"
              />
              <MetricCard
                icon="🔄"
                label="Counter Offers"
                value={data.negotiations.status_breakdown.countered.toString()}
                color="gold"
              />
            </div>

            {/* Discount Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="glass rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span>📊</span> Discount Distribution
                </h3>
                <div className="space-y-4">
                  {Object.entries(data.negotiations.discount_distribution).map(([range, count]) => (
                    <div key={range} className="flex items-center gap-4">
                      <span className="w-16 text-sm text-gray-400">{range}</span>
                      <div className="flex-1 h-8 bg-white/5 rounded-lg overflow-hidden relative">
                        <div 
                          className="h-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-1000 flex items-center justify-end pr-2"
                          style={{ width: `${Math.min((count / data.negotiations.total_offers) * 100 * 3, 100)}%` }}
                        >
                          <span className="text-xs font-bold">{count}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Platform Negotiation Stats */}
              <div className="glass rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span>🏪</span> Platform Success Rates
                </h3>
                <div className="space-y-4">
                  {data.negotiations.platform_stats.map((platform) => (
                    <div key={platform.platform} className="p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium capitalize">{platform.platform}</span>
                        <span className="text-[#00D9A5] font-bold">{platform.success_rate}%</span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-400">
                        <span>{platform.total_offers} offers</span>
                        <span>•</span>
                        <span>Avg {platform.avg_discount}% discount</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Savings Summary */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                <span>💰</span> Savings Summary
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-6 bg-gradient-to-br from-[#00D9A5]/20 to-[#00B894]/20 rounded-xl border border-[#00D9A5]/30">
                  <div className="text-4xl font-bold text-[#00D9A5]">₹{data.savings.total_savings.toLocaleString()}</div>
                  <div className="text-gray-400 mt-2">Total Savings</div>
                </div>
                <div className="text-center p-6 bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-xl border border-purple-500/30">
                  <div className="text-4xl font-bold text-purple-400">{data.savings.avg_savings_percent}%</div>
                  <div className="text-gray-400 mt-2">Avg Savings %</div>
                </div>
                <div className="text-center p-6 bg-gradient-to-br from-amber-500/20 to-amber-600/20 rounded-xl border border-amber-500/30">
                  <div className="text-4xl font-bold text-amber-400">₹{data.negotiations.avg_savings_per_deal}</div>
                  <div className="text-gray-400 mt-2">Avg per Deal</div>
                </div>
              </div>
            </div>

            {/* Top Savings Products */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <span>🎯</span> Top Savings Products
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.savings.top_products.slice(0, 6).map((product, index) => (
                  <div key={product.product} className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                    <div className="w-10 h-10 rounded-lg bg-[#00D9A5]/20 flex items-center justify-center font-bold text-[#00D9A5]">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium line-clamp-1">{product.product}</div>
                      <div className="text-sm text-gray-400">{product.deals} deals</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-[#00D9A5]">₹{product.total_savings}</div>
                      <div className="text-xs text-gray-500">saved</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Platforms Tab */}
        {activeTab === 'platforms' && (
          <div className="space-y-8">
            {/* Platform Status */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                <span>⚡</span> Platform Status (Real-time)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {Object.entries(data.realtime.platform_status).map(([platform, status]) => (
                  <div key={platform} className="p-4 bg-white/5 rounded-xl text-center">
                    <div className="text-3xl mb-2">
                      {platform === 'blinkit' && '🟡'}
                      {platform === 'zepto' && '🟣'}
                      {platform === 'instamart' && '🟠'}
                      {platform === 'bigbasket' && '🟢'}
                      {platform === 'jiomart' && '🔵'}
                    </div>
                    <div className="font-medium capitalize mb-1">{platform}</div>
                    <div className={`text-xs px-2 py-1 rounded-full inline-block ${
                      status.status === 'online' 
                        ? 'bg-[#00D9A5]/20 text-[#00D9A5]' 
                        : 'bg-red-500/20 text-red-400'
                    }`}>
                      {status.status}
                    </div>
                    <div className="text-gray-500 text-sm mt-2">{status.latency}ms</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Platform Comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="glass rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span>🏆</span> Best Price Wins
                </h3>
                <div className="space-y-4">
                  {data.platforms.platforms.map((platform) => (
                    <div key={platform.platform_id} className="flex items-center gap-4">
                      <div 
                        className="w-12 h-12 rounded-xl flex items-center justify-center text-xl"
                        style={{ backgroundColor: platform.color + '20' }}
                      >
                        {platform.logo}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium">{platform.platform_name}</div>
                        <div className="text-sm text-gray-400">{platform.wins.toLocaleString()} wins</div>
                      </div>
                      <div className="text-2xl font-bold" style={{ color: platform.color }}>
                        {platform.win_percentage}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="glass rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <span>💰</span> Savings by Platform
                </h3>
                <div className="space-y-4">
                  {data.savings.platform_savings.map((platform) => (
                    <div key={platform.platform} className="p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium capitalize">{platform.platform}</span>
                        <span className="text-[#00D9A5] font-bold">₹{platform.total_savings}</span>
                      </div>
                      <div className="text-sm text-gray-400">
                        {platform.deal_count} deals
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Conversions Tab */}
        {activeTab === 'conversions' && (
          <div className="space-y-8">
            {/* Conversion Funnel */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                <span>📈</span> Conversion Funnel (24 hours)
              </h3>
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <FunnelStep
                  label="Searches"
                  value={data.conversions.funnel.searches}
                  percentage={100}
                  color="#8B5CF6"
                />
                <FunnelArrow rate={data.conversions.conversion_rates.search_to_order} />
                <FunnelStep
                  label="Order Intents"
                  value={data.conversions.funnel.order_intents}
                  percentage={data.conversions.conversion_rates.search_to_order}
                  color="#F59E0B"
                />
                <FunnelArrow rate={data.conversions.conversion_rates.search_to_negotiate} />
                <FunnelStep
                  label="Negotiations"
                  value={data.conversions.funnel.negotiations_started}
                  percentage={data.conversions.conversion_rates.search_to_negotiate}
                  color="#00D9A5"
                />
                <FunnelArrow rate={data.conversions.conversion_rates.negotiate_to_deal} />
                <FunnelStep
                  label="Deals Completed"
                  value={data.conversions.funnel.deals_completed}
                  percentage={data.conversions.conversion_rates.negotiate_to_deal}
                  color="#10B981"
                />
              </div>
            </div>

            {/* Conversion Rates */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ConversionCard
                title="Search → Order"
                rate={data.conversions.conversion_rates.search_to_order}
                description="Users who showed intent to order after searching"
              />
              <ConversionCard
                title="Search → Negotiate"
                rate={data.conversions.conversion_rates.search_to_negotiate}
                description="Users who started negotiating after searching"
              />
              <ConversionCard
                title="Negotiate → Deal"
                rate={data.conversions.conversion_rates.negotiate_to_deal}
                description="Negotiations that resulted in completed deals"
              />
            </div>

            {/* Daily Savings Trend */}
            {data.savings.daily_trend.length > 0 && (
              <div className="glass rounded-2xl p-6">
                <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <span>📅</span> Daily Savings Trend
                </h3>
                <div className="flex items-end gap-4 h-48">
                  {data.savings.daily_trend.map((day, index) => {
                    const maxSavings = Math.max(...data.savings.daily_trend.map(d => d.savings));
                    const height = maxSavings > 0 ? (day.savings / maxSavings) * 100 : 0;
                    return (
                      <div key={day.date} className="flex-1 flex flex-col items-center gap-2">
                        <div className="text-xs text-[#00D9A5] font-mono">₹{day.savings}</div>
                        <div 
                          className="w-full bg-gradient-to-t from-[#00D9A5] to-[#00B894] rounded-t-lg transition-all duration-500"
                          style={{ height: `${Math.max(height, 10)}%` }}
                        />
                        <div className="text-xs text-gray-500">{day.date.slice(5)}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

// Metric Card Component
function MetricCard({ icon, label, value, subtext, color }: {
  icon: string;
  label: string;
  value: string;
  subtext?: string;
  color: 'purple' | 'mint' | 'gold' | 'blue' | 'coral';
}) {
  const colors = {
    purple: 'from-purple-500/20 to-purple-600/20 border-purple-500/30',
    mint: 'from-[#00D9A5]/20 to-[#00B894]/20 border-[#00D9A5]/30',
    gold: 'from-amber-500/20 to-amber-600/20 border-amber-500/30',
    blue: 'from-blue-500/20 to-blue-600/20 border-blue-500/30',
    coral: 'from-red-500/20 to-red-600/20 border-red-500/30',
  };
  
  const textColors = {
    purple: 'text-purple-400',
    mint: 'text-[#00D9A5]',
    gold: 'text-amber-400',
    blue: 'text-blue-400',
    coral: 'text-red-400',
  };

  return (
    <div className={`p-5 rounded-2xl bg-gradient-to-br ${colors[color]} border`}>
      <div className="text-3xl mb-2">{icon}</div>
      <div className={`text-2xl font-bold ${textColors[color]}`}>{value}</div>
      <div className="text-sm text-gray-400">{label}</div>
      {subtext && <div className="text-xs text-gray-500 mt-1">{subtext}</div>}
    </div>
  );
}

// Funnel Step Component
function FunnelStep({ label, value, percentage, color }: {
  label: string;
  value: number;
  percentage: number;
  color: string;
}) {
  return (
    <div className="flex-1 text-center">
      <div 
        className="w-24 h-24 mx-auto rounded-2xl flex flex-col items-center justify-center mb-3"
        style={{ backgroundColor: color + '20', borderColor: color, borderWidth: 2 }}
      >
        <div className="text-2xl font-bold" style={{ color }}>{value}</div>
      </div>
      <div className="font-medium">{label}</div>
      <div className="text-sm text-gray-500">{percentage.toFixed(1)}%</div>
    </div>
  );
}

// Funnel Arrow Component
function FunnelArrow({ rate }: { rate: number }) {
  return (
    <div className="hidden md:flex items-center gap-2 text-gray-500">
      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
      </svg>
      <span className="text-xs font-mono text-[#00D9A5]">{rate.toFixed(1)}%</span>
    </div>
  );
}

// Conversion Card Component
function ConversionCard({ title, rate, description }: {
  title: string;
  rate: number;
  description: string;
}) {
  const getColor = (rate: number) => {
    if (rate >= 50) return 'text-[#00D9A5]';
    if (rate >= 25) return 'text-amber-400';
    return 'text-red-400';
  };

  return (
    <div className="glass rounded-2xl p-6">
      <h4 className="font-medium mb-2">{title}</h4>
      <div className={`text-4xl font-bold mb-2 ${getColor(rate)}`}>
        {rate.toFixed(1)}%
      </div>
      <p className="text-sm text-gray-500">{description}</p>
      <div className="mt-4 h-2 bg-white/10 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-[#00D9A5] to-[#00B894] rounded-full transition-all duration-1000"
          style={{ width: `${Math.min(rate, 100)}%` }}
        />
      </div>
    </div>
  );
}
