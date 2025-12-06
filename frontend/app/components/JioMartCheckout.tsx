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
}

interface Product {
  product_id: string;
  product_name: string;
  brand: string | null;
  quantity: string;
  lowest_price: number;
  prices: PriceEntry[];
}

interface JioMartCheckoutProps {
  product: Product;
  onClose: () => void;
  onSuccess?: (orderId: string) => void;
}

interface JioMartUser {
  user_id: string;
  name: string;
  phone: string;
}

interface Address {
  id: string;
  name: string;
  address: string;
  pincode: string;
  is_default: boolean;
}

type Step = 'login' | 'otp' | 'address' | 'payment' | 'confirm' | 'success' | 'error';

export default function JioMartCheckout({ product, onClose, onSuccess }: JioMartCheckoutProps) {
  const [step, setStep] = useState<Step>('login');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Login state
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [user, setUser] = useState<JioMartUser | null>(null);
  
  // Order state
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [selectedAddress, setSelectedAddress] = useState<string | null>(null);
  const [paymentMethod, setPaymentMethod] = useState('cod');
  const [quantity, setQuantity] = useState(1);
  
  // Order result
  const [orderId, setOrderId] = useState<string | null>(null);
  
  // Check if already logged in
  useEffect(() => {
    checkLoginStatus();
  }, []);
  
  const checkLoginStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/jiomart/status`);
      const data = await response.json();
      
      if (data.logged_in && data.user) {
        setUser(data.user);
        setStep('address');
        fetchAddresses();
      }
    } catch (e) {
      console.error('Status check error:', e);
    }
  };
  
  const fetchAddresses = async () => {
    try {
      const response = await fetch(`${API_URL}/api/jiomart/addresses`);
      const data = await response.json();
      setAddresses(data.addresses || []);
      
      // Auto-select default address
      const defaultAddr = data.addresses?.find((a: Address) => a.is_default);
      if (defaultAddr) {
        setSelectedAddress(defaultAddr.id);
      }
    } catch (e) {
      console.error('Fetch addresses error:', e);
    }
  };
  
  const handleSendOTP = async () => {
    if (!phone || phone.length !== 10) {
      setError('Please enter a valid 10-digit phone number');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/api/jiomart/send-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSessionId(data.session_id);
        setStep('otp');
      } else {
        setError(data.error || 'Failed to send OTP');
      }
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleVerifyOTP = async () => {
    if (!otp || otp.length !== 6) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/api/jiomart/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, otp, session_id: sessionId })
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setStep('address');
        fetchAddresses();
      } else {
        setError('Invalid OTP. Please try again.');
      }
    } catch (e) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handlePlaceOrder = async () => {
    if (!selectedAddress) {
      setError('Please select a delivery address');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setStep('confirm');
    
    try {
      const response = await fetch(`${API_URL}/api/jiomart/one-click-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: product.product_id,
          product_name: product.product_name,
          quantity,
          address_id: selectedAddress,
          payment_method: paymentMethod
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrderId(data.order_id);
        setStep('success');
        onSuccess?.(data.order_id);
      } else {
        const data = await response.json();
        setError(data.detail || 'Order failed');
        setStep('error');
      }
    } catch (e) {
      setError('Network error. Please try again.');
      setStep('error');
    } finally {
      setIsLoading(false);
    }
  };
  
  const jioPrice = product.prices.find(p => p.platform === 'jiomart');
  const totalAmount = (jioPrice?.price || product.lowest_price) * quantity;
  
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
        <div className="bg-gradient-to-r from-blue-600/30 to-blue-700/30 p-5 border-b border-white/10">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center text-white text-xl font-bold">
                J
              </div>
              <div>
                <h2 className="font-display text-xl font-bold">JioMart Direct</h2>
                <p className="text-gray-400 text-sm">One-Click Checkout</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg">
              ✕
            </button>
          </div>
        </div>
        
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
            <div className="text-right">
              <div className="text-lg font-bold text-green-400">₹{totalAmount}</div>
              <div className="flex items-center gap-1 mt-1">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="w-6 h-6 rounded bg-white/10 text-xs"
                >-</button>
                <span className="w-6 text-center text-sm">{quantity}</span>
                <button
                  onClick={() => setQuantity(Math.min(10, quantity + 1))}
                  className="w-6 h-6 rounded bg-white/10 text-xs"
                >+</button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Error Display */}
        {error && (
          <div className="mx-4 mt-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}
        
        {/* Step Content */}
        <div className="p-4">
          {/* Login Step */}
          {step === 'login' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Mobile Number</label>
                <div className="flex items-center gap-2">
                  <span className="bg-white/10 px-3 py-3 rounded-lg text-gray-400">+91</span>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                    placeholder="Enter 10-digit mobile"
                    className="flex-1 bg-white/10 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500"
                    maxLength={10}
                  />
                </div>
              </div>
              
              <button
                onClick={handleSendOTP}
                disabled={isLoading || phone.length !== 10}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg font-medium transition-all"
              >
                {isLoading ? 'Sending...' : 'Send OTP'}
              </button>
              
              <p className="text-xs text-gray-500 text-center">
                We&apos;ll send an OTP to verify your JioMart account
              </p>
            </div>
          )}
          
          {/* OTP Step */}
          {step === 'otp' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Enter OTP</label>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  placeholder="6-digit OTP"
                  className="w-full bg-white/10 border border-white/10 rounded-lg px-4 py-3 text-center text-2xl tracking-widest focus:outline-none focus:border-blue-500"
                  maxLength={6}
                />
                <p className="text-xs text-gray-500 mt-2 text-center">
                  OTP sent to +91 {phone}
                </p>
              </div>
              
              <button
                onClick={handleVerifyOTP}
                disabled={isLoading || otp.length !== 6}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg font-medium transition-all"
              >
                {isLoading ? 'Verifying...' : 'Verify OTP'}
              </button>
              
              <button
                onClick={() => { setOtp(''); handleSendOTP(); }}
                className="w-full py-2 text-blue-400 hover:text-blue-300 text-sm"
              >
                Resend OTP
              </button>
            </div>
          )}
          
          {/* Address & Payment Step */}
          {step === 'address' && (
            <div className="space-y-4">
              <div className="text-sm text-gray-400 mb-2">
                Logged in as: <span className="text-white">{user?.name || user?.phone}</span>
              </div>
              
              {/* Address Selection */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Delivery Address</label>
                {addresses.length > 0 ? (
                  <div className="space-y-2">
                    {addresses.map((addr) => (
                      <button
                        key={addr.id}
                        onClick={() => setSelectedAddress(addr.id)}
                        className={`w-full p-3 rounded-lg text-left transition-all ${
                          selectedAddress === addr.id
                            ? 'bg-blue-500/20 border-2 border-blue-500'
                            : 'bg-white/5 border border-white/10 hover:bg-white/10'
                        }`}
                      >
                        <div className="font-medium text-sm">{addr.name}</div>
                        <div className="text-xs text-gray-400 mt-1">{addr.address}</div>
                        <div className="text-xs text-gray-500">{addr.pincode}</div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 text-sm text-yellow-400">
                    No saved addresses. Please add an address in JioMart app first.
                  </div>
                )}
              </div>
              
              {/* Payment Method */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Payment Method</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { id: 'cod', name: 'Cash on Delivery', icon: '💵' },
                    { id: 'upi', name: 'UPI', icon: '📱' },
                    { id: 'card', name: 'Card', icon: '💳' },
                    { id: 'wallet', name: 'Wallet', icon: '👛' }
                  ].map((method) => (
                    <button
                      key={method.id}
                      onClick={() => setPaymentMethod(method.id)}
                      className={`p-3 rounded-lg text-center transition-all ${
                        paymentMethod === method.id
                          ? 'bg-blue-500/20 border-2 border-blue-500'
                          : 'bg-white/5 border border-white/10 hover:bg-white/10'
                      }`}
                    >
                      <div className="text-xl mb-1">{method.icon}</div>
                      <div className="text-xs">{method.name}</div>
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Order Summary */}
              <div className="bg-white/5 rounded-lg p-3">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">Subtotal</span>
                  <span>₹{totalAmount}</span>
                </div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">Delivery</span>
                  <span className="text-green-400">FREE</span>
                </div>
                <div className="flex justify-between font-bold pt-2 border-t border-white/10">
                  <span>Total</span>
                  <span className="text-green-400">₹{totalAmount}</span>
                </div>
              </div>
              
              <button
                onClick={handlePlaceOrder}
                disabled={!selectedAddress}
                className="w-full py-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-600 disabled:to-gray-700 rounded-xl font-bold text-lg transition-all"
              >
                🛒 Place Order - ₹{totalAmount}
              </button>
            </div>
          )}
          
          {/* Confirm Step (Loading) */}
          {step === 'confirm' && (
            <div className="py-8 text-center">
              <div className="w-16 h-16 mx-auto mb-4 relative">
                <div className="absolute inset-0 bg-blue-500/20 rounded-full animate-ping" />
                <div className="relative w-full h-full bg-blue-500/30 rounded-full flex items-center justify-center text-3xl">
                  🛒
                </div>
              </div>
              <h3 className="text-lg font-bold mb-2">Placing your order...</h3>
              <p className="text-gray-400 text-sm">Please wait while we process</p>
            </div>
          )}
          
          {/* Success Step */}
          {step === 'success' && (
            <div className="py-8 text-center">
              <div className="w-20 h-20 mx-auto mb-4 bg-green-500/20 rounded-full flex items-center justify-center text-4xl">
                ✓
              </div>
              <h3 className="text-xl font-bold text-green-400 mb-2">Order Placed!</h3>
              <p className="text-gray-400 mb-4">
                Order ID: <span className="text-white font-mono">{orderId}</span>
              </p>
              <div className="bg-white/5 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-400">
                  Your order has been placed successfully on JioMart.
                  You&apos;ll receive a confirmation SMS shortly.
                </p>
              </div>
              <button
                onClick={onClose}
                className="w-full py-3 bg-green-600 hover:bg-green-700 rounded-lg font-medium"
              >
                Done
              </button>
            </div>
          )}
          
          {/* Error Step */}
          {step === 'error' && (
            <div className="py-8 text-center">
              <div className="w-20 h-20 mx-auto mb-4 bg-red-500/20 rounded-full flex items-center justify-center text-4xl">
                ✕
              </div>
              <h3 className="text-xl font-bold text-red-400 mb-2">Order Failed</h3>
              <p className="text-gray-400 mb-4">{error || 'Something went wrong'}</p>
              <div className="space-y-2">
                <button
                  onClick={() => setStep('address')}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium"
                >
                  Try Again
                </button>
                <button
                  onClick={onClose}
                  className="w-full py-2 text-gray-400 hover:text-white text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="p-4 bg-white/5 border-t border-white/10">
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
            <span>🔒</span>
            <span>Secure checkout powered by JioMart</span>
          </div>
        </div>
      </div>
    </div>
  );
}

