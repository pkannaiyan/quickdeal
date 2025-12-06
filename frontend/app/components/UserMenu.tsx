'use client';

import { useState, useRef, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  default_pincode: string;
  default_city: string;
}

interface UserMenuProps {
  user: User;
  onLogout: () => void;
}

export default function UserMenu({ user, onLogout }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  
  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  const initials = user.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : user.username.slice(0, 2).toUpperCase();
  
  return (
    <div className="relative" ref={menuRef}>
      {/* User Avatar Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-xl glass hover:bg-white/10 transition-colors"
      >
        <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center text-sm font-bold text-primary">
          {initials}
        </div>
        <span className="text-sm font-medium hidden sm:block">{user.username}</span>
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 glass rounded-xl border border-white/10 shadow-xl z-50 overflow-hidden">
          {/* User Info */}
          <div className="p-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-primary/30 flex items-center justify-center text-lg font-bold text-primary">
                {initials}
              </div>
              <div>
                <div className="font-semibold">{user.full_name || user.username}</div>
                <div className="text-sm text-gray-400">{user.email}</div>
              </div>
            </div>
            <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
              <span>📍</span>
              <span>{user.default_city} - {user.default_pincode}</span>
            </div>
          </div>
          
          {/* Dashboard Links */}
          <div className="py-2 border-b border-white/10">
            <MenuLink icon="🛒" label="Buyer Dashboard" href="/buyer" />
            <MenuLink icon="🏪" label="Seller Dashboard" href="/seller" />
            <MenuLink icon="👑" label="Admin Panel" href="/admin" />
            <MenuLink icon="📊" label="Analytics" href="/dashboard" />
          </div>
          
          {/* Menu Items */}
          <div className="py-2">
            <MenuLink icon="🔔" label="Price Alerts" href="/alerts" />
            <MenuLink icon="❤️" label="Saved Products" href="/saved" />
            <MenuLink icon="⚙️" label="Settings" href="/settings" />
          </div>
          
          {/* Logout */}
          <div className="p-2 border-t border-white/10">
            <button
              onClick={onLogout}
              className="w-full flex items-center gap-3 px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
            >
              <span>🚪</span>
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function MenuLink({ 
  icon, 
  label, 
  href, 
  badge 
}: { 
  icon: string; 
  label: string; 
  href: string; 
  badge?: number;
}) {
  return (
    <a
      href={href}
      className="flex items-center justify-between px-4 py-2 hover:bg-white/5 transition-colors"
    >
      <div className="flex items-center gap-3">
        <span>{icon}</span>
        <span className="text-sm">{label}</span>
      </div>
      {badge !== undefined && badge > 0 && (
        <span className="bg-primary/30 text-primary text-xs px-2 py-0.5 rounded-full">
          {badge}
        </span>
      )}
    </a>
  );
}

