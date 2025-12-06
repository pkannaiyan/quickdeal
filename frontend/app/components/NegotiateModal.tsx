'use client';

import { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

interface PriceEntry {
  platform: string;
  platform_name: string;
  price: number;
  mrp: number;
  discount_percent: number;
  is_available: boolean;
}

interface Product {
  product_id: string;
  product_name: string;
  brand: string | null;
  quantity: string;
  lowest_price: number;
  prices: PriceEntry[];
}

interface NegotiateModalProps {
  product: Product;
  selectedPlatform?: string;
  onClose: () => void;
  onSuccess?: (offerId: string) => void;
}

export default function NegotiateModal({ 
  product, 
  selectedPlatform, 
  onClose, 
  onSuccess 
}: NegotiateModalProps) {
  const [platform, setPlatform] = useState(selectedPlatform || '');
  const [offeredPrice, setOfferedPrice] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [offerId, setOfferId] = useState<string | null>(null);

  // Get selected platform price
  const platformPrice = product.prices.find(p => p.platform === platform);
  const originalPrice = platformPrice?.price || product.lowest_price;
  
  // Calculate discount
  const discount = offeredPrice 
    ? ((originalPrice - parseFloat(offeredPrice)) / originalPrice * 100)
    : 0;

  // Preset discount options
  const discountPresets = [5, 10, 15, 20];

  useEffect(() => {
    // Default to best platform if not selected
    if (!platform && product.prices.length > 0) {
      const bestPrice = product.prices
        .filter(p => p.is_available)
        .sort((a, b) => a.price - b.price)[0];
      if (bestPrice) {
        setPlatform(bestPrice.platform);
      }
    }
  }, [product.prices, platform]);

  const applyDiscount = (discountPercent: number) => {
    const newPrice = originalPrice * (1 - discountPercent / 100);
    setOfferedPrice(newPrice.toFixed(0));
  };

  const handleSubmit = async () => {
    if (!platform || !offeredPrice) {
      setError('Please select platform and enter offer price');
      return;
    }

    const price = parseFloat(offeredPrice);
    if (price >= originalPrice) {
      setError('Offer price must be less than original price');
      return;
    }

    if (discount > 50) {
      setError('Maximum 50% discount allowed');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const userId = localStorage.getItem('userId') || `buyer_${Date.now()}`;
      const userName = localStorage.getItem('userName') || 'Guest Buyer';
      
      // Save user ID if not exists
      if (!localStorage.getItem('userId')) {
        localStorage.setItem('userId', userId);
      }

      const response = await fetch(`${API_URL}/api/negotiate/offers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': userId,
          'X-User-Name': userName
        },
        body: JSON.stringify({
          product_id: product.product_id,
          product_name: product.product_name,
          product_brand: product.brand,
          product_quantity: product.quantity,
          platform: platform,
          platform_name: platformPrice?.platform_name || platform,
          original_price: originalPrice,
          offered_price: price,
          quantity: quantity,
          message: message || undefined
        })
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        setOfferId(data.offer?.offer_id);
        onSuccess?.(data.offer?.offer_id);
      } else {
        setError(data.detail || 'Failed to submit offer');
      }
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="glass rounded-2xl max-w-md w-full overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600/30 to-pink-600/30 p-5 border-b border-white/10">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-500/30 rounded-xl flex items-center justify-center text-2xl">
                🤝
              </div>
              <div>
                <h2 className="font-display text-xl font-bold">Make an Offer</h2>
                <p className="text-gray-400 text-sm">Negotiate for a better price</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg">
              ✕
            </button>
          </div>
        </div>

        {success ? (
          /* Success State */
          <div className="p-8 text-center">
            <div className="w-20 h-20 mx-auto mb-4 bg-green-500/20 rounded-full flex items-center justify-center text-4xl">
              ✓
            </div>
            <h3 className="text-xl font-bold text-green-400 mb-2">Offer Submitted!</h3>
            <p className="text-gray-400 mb-4">
              Your offer has been sent to the seller. You&apos;ll be notified when they respond.
            </p>
            <div className="bg-white/5 rounded-lg p-4 mb-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Your Offer:</span>
                  <span className="ml-2 font-bold text-green-400">₹{offeredPrice}</span>
                </div>
                <div>
                  <span className="text-gray-500">Discount:</span>
                  <span className="ml-2 text-purple-400">{discount.toFixed(0)}%</span>
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="flex-1 py-3 bg-white/10 hover:bg-white/20 rounded-lg"
              >
                Close
              </button>
              <a
                href="/buyer"
                className="flex-1 py-3 bg-purple-500 hover:bg-purple-600 rounded-lg text-center"
              >
                View Offers
              </a>
            </div>
          </div>
        ) : (
          <>
            {/* Product Info */}
            <div className="p-4 bg-white/5 border-b border-white/10">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-white/10 rounded-xl flex items-center justify-center text-2xl">
                  🛍️
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium line-clamp-2 text-sm">{product.product_name}</h3>
                  <div className="text-gray-400 text-xs mt-1">
                    {product.brand} • {product.quantity}
                  </div>
                </div>
              </div>
            </div>

            {/* Form */}
            <div className="p-5 space-y-4">
              {/* Platform Selection */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Select Platform</label>
                <div className="grid grid-cols-2 gap-2">
                  {product.prices
                    .filter(p => p.is_available)
                    .sort((a, b) => a.price - b.price)
                    .map((p) => (
                      <button
                        key={p.platform}
                        onClick={() => {
                          setPlatform(p.platform);
                          setOfferedPrice('');
                        }}
                        className={`p-3 rounded-lg text-left transition-all ${
                          platform === p.platform
                            ? 'bg-purple-500/20 border-2 border-purple-500'
                            : 'bg-white/5 border border-white/10 hover:bg-white/10'
                        }`}
                      >
                        <div className="font-medium text-sm">{p.platform_name}</div>
                        <div className="text-green-400 font-bold">₹{p.price}</div>
                      </button>
                    ))}
                </div>
              </div>

              {/* Quick Discount Options */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Quick Discount</label>
                <div className="flex gap-2">
                  {discountPresets.map((d) => (
                    <button
                      key={d}
                      onClick={() => applyDiscount(d)}
                      className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                        Math.abs(discount - d) < 1
                          ? 'bg-purple-500 text-white'
                          : 'bg-white/10 hover:bg-white/20'
                      }`}
                    >
                      {d}% off
                    </button>
                  ))}
                </div>
              </div>

              {/* Custom Offer Price */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Your Offer Price</label>
                <div className="flex items-center gap-3">
                  <div className="relative flex-1">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">₹</span>
                    <input
                      type="number"
                      value={offeredPrice}
                      onChange={(e) => setOfferedPrice(e.target.value)}
                      placeholder={`Max ₹${originalPrice}`}
                      className="w-full bg-white/10 border border-white/10 rounded-lg pl-8 pr-4 py-3 text-lg focus:outline-none focus:border-purple-500"
                    />
                  </div>
                  {offeredPrice && (
                    <div className={`text-lg font-bold ${discount > 30 ? 'text-red-400' : 'text-purple-400'}`}>
                      -{discount.toFixed(0)}%
                    </div>
                  )}
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Original: ₹{originalPrice}</span>
                  {offeredPrice && (
                    <span className="text-green-400">
                      Save ₹{(originalPrice - parseFloat(offeredPrice)).toFixed(0)}
                    </span>
                  )}
                </div>
              </div>

              {/* Quantity */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Quantity</label>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-lg text-lg"
                  >
                    -
                  </button>
                  <span className="w-12 text-center text-lg font-bold">{quantity}</span>
                  <button
                    onClick={() => setQuantity(Math.min(10, quantity + 1))}
                    className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-lg text-lg"
                  >
                    +
                  </button>
                  {offeredPrice && (
                    <span className="ml-auto text-gray-400">
                      Total: <span className="text-green-400 font-bold">₹{(parseFloat(offeredPrice) * quantity).toFixed(0)}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Message */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Message (optional)</label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="e.g., Buying in bulk, please offer discount..."
                  rows={2}
                  className="w-full bg-white/10 border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-purple-500"
                />
              </div>

              {/* Error */}
              {error && (
                <div className="p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm">
                  {error}
                </div>
              )}

              {/* Submit */}
              <button
                onClick={handleSubmit}
                disabled={loading || !offeredPrice || parseFloat(offeredPrice) >= originalPrice}
                className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-gray-600 disabled:to-gray-700 rounded-xl font-bold text-lg transition-all"
              >
                {loading ? 'Submitting...' : '🤝 Submit Offer'}
              </button>

              <p className="text-xs text-gray-500 text-center">
                Seller will respond within 24 hours. Auto-expires if no response.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

