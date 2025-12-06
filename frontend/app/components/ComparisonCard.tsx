'use client';

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

interface ComparisonCardProps {
  product: Product;
  onClick: () => void;
  onQuickOrder?: () => void;
  onOneClickCheckout?: () => void;
  onNegotiate?: () => void;
  isSelected: boolean;
}

const PLATFORM_COLORS: Record<string, string> = {
  'blinkit': 'from-yellow-400 to-yellow-500',
  'zepto': 'from-purple-500 to-purple-600',
  'instamart': 'from-orange-500 to-orange-600',
  'bigbasket': 'from-lime-500 to-lime-600',
  'jiomart': 'from-blue-500 to-blue-600',
};

export default function ComparisonCard({ product, onClick, onQuickOrder, onOneClickCheckout, onNegotiate, isSelected }: ComparisonCardProps) {
  const hasSavings = product.savings_percent >= 5;
  const bestPrice = product.prices.find(p => p.price === product.lowest_price);
  
  return (
    <div
      onClick={onClick}
      className={`group relative glass rounded-2xl overflow-hidden cursor-pointer card-hover ${
        isSelected ? 'ring-2 ring-[#00D9A5]' : ''
      } ${hasSavings ? 'deal-highlight' : ''}`}
    >
      {/* Savings Banner */}
      {hasSavings && (
        <div className="absolute top-3 right-3 z-10">
          <div className="gradient-mint px-3 py-1.5 rounded-full text-xs font-bold text-black flex items-center gap-1 savings-pulse">
            <span>🔥</span>
            <span>Save {product.savings_percent.toFixed(0)}%</span>
          </div>
        </div>
      )}

      {/* Product Image Section */}
      <div className="relative h-48 bg-gradient-to-br from-gray-800/50 to-gray-900/50 flex items-center justify-center overflow-hidden">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.product_name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            onError={(e) => {
              (e.target as HTMLImageElement).src = `https://via.placeholder.com/300x200.png?text=${encodeURIComponent(product.product_name.slice(0, 10))}`;
            }}
          />
        ) : (
          <div className="text-6xl opacity-50">📦</div>
        )}
        
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0A0F1C] via-transparent to-transparent" />
        
        {/* Platform availability badges */}
        <div className="absolute bottom-3 left-3 flex gap-1">
          {product.prices.slice(0, 4).map((price) => (
            <div
              key={price.platform}
              className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm bg-gradient-to-br ${
                PLATFORM_COLORS[price.platform] || 'from-gray-500 to-gray-600'
              } ${!price.is_available ? 'opacity-30' : ''} shadow-lg`}
              title={`${price.platform_name}: ₹${price.price}`}
            >
              {price.platform_logo}
            </div>
          ))}
          {product.prices.length > 4 && (
            <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs bg-white/10 backdrop-blur">
              +{product.prices.length - 4}
            </div>
          )}
        </div>
      </div>

      {/* Content Section */}
      <div className="p-5">
        {/* Product Info */}
        <div className="mb-4">
          <h3 className="font-semibold text-lg leading-tight line-clamp-2 group-hover:text-[#00D9A5] transition-colors">
            {product.product_name}
          </h3>
          <div className="flex items-center gap-2 mt-2 text-sm text-gray-400">
            {product.brand && (
              <>
                <span className="badge badge-info">{product.brand}</span>
                <span>•</span>
              </>
            )}
            <span>{product.quantity}</span>
          </div>
        </div>

        {/* Price Comparison */}
        <div className="flex items-end justify-between mb-4">
          <div>
            <div className="text-xs text-gray-500 mb-1">Best Price</div>
            <div className="text-3xl font-bold font-price text-[#00D9A5] price-pop">
              ₹{product.lowest_price}
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500 mb-1">Highest</div>
            <div className="text-lg text-gray-500 line-through font-price">
              ₹{product.highest_price}
            </div>
          </div>
        </div>

        {/* Best Platform Info */}
        <div className={`p-3 rounded-xl bg-gradient-to-r ${PLATFORM_COLORS[product.best_platform] || 'from-gray-600 to-gray-700'} bg-opacity-20 border border-white/10 mb-4`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xl">{product.best_platform_logo}</span>
              <div>
                <div className="font-medium text-sm">{product.best_platform}</div>
                <div className="text-xs text-white/70">{product.best_delivery_time}</div>
              </div>
            </div>
            <div className="badge badge-success">Best Deal</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2">
          {/* Primary - One Click Buy */}
          {onOneClickCheckout && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onOneClickCheckout();
              }}
              className="w-full py-3.5 btn-primary rounded-xl font-bold text-sm flex items-center justify-center gap-2"
            >
              <span>⚡</span>
              Buy Now @ ₹{product.lowest_price}
            </button>
          )}
          
          {/* Secondary Actions */}
          <div className="grid grid-cols-2 gap-2">
            {onNegotiate && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onNegotiate();
                }}
                className="py-2.5 btn-secondary rounded-xl text-sm flex items-center justify-center gap-1.5"
              >
                <span>🤝</span>
                Negotiate
              </button>
            )}
            
            {onQuickOrder && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onQuickOrder();
                }}
                className="py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-sm flex items-center justify-center gap-1.5 transition-all"
              >
                <span>🔗</span>
                Compare
              </button>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-gray-500">
          <span>{product.available_on} platforms</span>
          <span className="flex items-center gap-1 text-[#00D9A5]">
            View details
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </div>
      </div>
    </div>
  );
}
