'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

type UserRole = 'buyer' | 'seller' | 'admin';

interface LoginCredentials {
  email: string;
  password: string;
}

// Demo users for quick login
const DEMO_USERS = {
  admin: { email: 'admin', password: 'admin', role: 'admin' as UserRole, name: 'Admin User' },
  buyer: { email: 'buyer@demo.com', password: 'buyer123', role: 'buyer' as UserRole, name: 'Demo Buyer' },
  seller_blinkit: { email: 'seller@blinkit.com', password: 'seller123', role: 'seller' as UserRole, name: 'Blinkit Seller', platform: 'blinkit' },
  seller_zepto: { email: 'seller@zepto.com', password: 'seller123', role: 'seller' as UserRole, name: 'Zepto Seller', platform: 'zepto' },
};

export default function LoginPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<UserRole>('buyer');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Check demo users first
      let user = null;
      
      // Admin login
      if (email === 'admin' && password === 'admin') {
        user = DEMO_USERS.admin;
      }
      // Buyer demo login
      else if (email === DEMO_USERS.buyer.email && password === DEMO_USERS.buyer.password) {
        user = DEMO_USERS.buyer;
      }
      // Seller demo logins
      else if (email === DEMO_USERS.seller_blinkit.email && password === DEMO_USERS.seller_blinkit.password) {
        user = { ...DEMO_USERS.seller_blinkit };
      }
      else if (email === DEMO_USERS.seller_zepto.email && password === DEMO_USERS.seller_zepto.password) {
        user = { ...DEMO_USERS.seller_zepto };
      }
      // Generic login for demo purposes
      else if (password.length >= 4) {
        // Allow any login for demo - determine role from tab
        user = {
          email,
          password,
          role: activeTab,
          name: email.split('@')[0] || 'User',
          platform: activeTab === 'seller' ? 'blinkit' : undefined
        };
      }

      if (user) {
        // Store user info in localStorage
        const userId = user.role === 'admin' ? 'admin' : 
                       user.role === 'seller' ? `user_${(user as any).platform || 'blinkit'}` :
                       `buyer_${Date.now()}`;
        
        localStorage.setItem('userId', userId);
        localStorage.setItem('userRole', user.role);
        localStorage.setItem('userName', user.name);
        localStorage.setItem('userEmail', user.email);
        if ((user as any).platform) {
          localStorage.setItem('sellerPlatform', (user as any).platform);
        }

        // Redirect based on role
        switch (user.role) {
          case 'admin':
            router.push('/admin');
            break;
          case 'seller':
            router.push('/seller');
            break;
          case 'buyer':
          default:
            router.push('/buyer');
            break;
        }
      } else {
        setError('Invalid credentials. Please try again.');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (userKey: keyof typeof DEMO_USERS) => {
    const user = DEMO_USERS[userKey];
    setEmail(user.email);
    setPassword(user.password);
    setActiveTab(user.role);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900/20 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-4">
            ← Back to Home
          </Link>
          <h1 className="text-3xl font-display font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            🛒 Price Compare
          </h1>
          <p className="text-gray-400 mt-2">Login to your account</p>
        </div>

        {/* Login Card */}
        <div className="glass rounded-2xl p-6">
          {/* Role Tabs */}
          <div className="flex gap-1 p-1 bg-white/5 rounded-xl mb-6">
            {(['buyer', 'seller', 'admin'] as UserRole[]).map((role) => (
              <button
                key={role}
                onClick={() => setActiveTab(role)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  activeTab === role
                    ? role === 'admin' 
                      ? 'bg-red-500 text-white'
                      : role === 'seller'
                      ? 'bg-emerald-500 text-white'
                      : 'bg-purple-500 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {role === 'buyer' && '🛒 '}
                {role === 'seller' && '🏪 '}
                {role === 'admin' && '👑 '}
                {role.charAt(0).toUpperCase() + role.slice(1)}
              </button>
            ))}
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                {activeTab === 'admin' ? 'Username' : 'Email'}
              </label>
              <input
                type={activeTab === 'admin' ? 'text' : 'email'}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={activeTab === 'admin' ? 'admin' : 'your@email.com'}
                className="w-full bg-white/10 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-white/10 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:border-indigo-500"
                required
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 rounded-xl font-bold text-lg transition-all ${
                activeTab === 'admin'
                  ? 'bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600'
                  : activeTab === 'seller'
                  ? 'bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600'
                  : 'bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600'
              } disabled:opacity-50`}
            >
              {loading ? 'Logging in...' : `Login as ${activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}`}
            </button>
          </form>

          {/* Quick Login */}
          <div className="mt-6 pt-6 border-t border-white/10">
            <p className="text-xs text-gray-500 text-center mb-3">Quick Demo Login:</p>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => quickLogin('buyer')}
                className="py-2 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 rounded-lg text-sm text-purple-400"
              >
                🛒 Demo Buyer
              </button>
              <button
                onClick={() => quickLogin('seller_blinkit')}
                className="py-2 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/30 rounded-lg text-sm text-emerald-400"
              >
                🏪 Blinkit Seller
              </button>
              <button
                onClick={() => quickLogin('seller_zepto')}
                className="py-2 bg-violet-500/20 hover:bg-violet-500/30 border border-violet-500/30 rounded-lg text-sm text-violet-400"
              >
                🏪 Zepto Seller
              </button>
              <button
                onClick={() => quickLogin('admin')}
                className="py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 rounded-lg text-sm text-red-400"
              >
                👑 Admin
              </button>
            </div>
          </div>

          {/* Demo Credentials Info */}
          <div className="mt-4 p-3 bg-white/5 rounded-lg text-xs text-gray-500">
            <p className="font-medium text-gray-400 mb-1">Demo Credentials:</p>
            <p>• Admin: <code className="text-gray-300">admin / admin</code></p>
            <p>• Buyer: <code className="text-gray-300">buyer@demo.com / buyer123</code></p>
            <p>• Seller: <code className="text-gray-300">seller@blinkit.com / seller123</code></p>
          </div>
        </div>
      </div>
    </div>
  );
}

