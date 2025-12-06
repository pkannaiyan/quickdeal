'use client';

import { useState, useRef, useEffect } from 'react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading?: boolean;
}

// Popular searches for suggestions
const POPULAR_SEARCHES = [
  'Milk', 'Bread', 'Eggs', 'Rice', 'Oil', 'Chips', 'Chocolate', 'Coffee', 'Tea', 'Sugar'
];

const CATEGORIES = [
  { icon: '🥛', label: 'Dairy', query: 'milk' },
  { icon: '🍞', label: 'Bread', query: 'bread' },
  { icon: '🥬', label: 'Veggies', query: 'vegetables' },
  { icon: '🍎', label: 'Fruits', query: 'fresh fruits' },
  { icon: '🍫', label: 'Snacks', query: 'chocolate chips' },
  { icon: '☕', label: 'Beverages', query: 'coffee tea' },
];

export default function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognitionAPI) {
        setVoiceSupported(true);
        recognitionRef.current = new SpeechRecognitionAPI();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = 'en-IN';

        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setQuery(transcript);
          onSearch(transcript);
          setIsListening(false);
        };

        recognitionRef.current.onerror = () => {
          setIsListening(false);
        };

        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }
    }
  }, [onSearch]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
      setShowSuggestions(false);
    }
  };

  const handleVoiceSearch = () => {
    if (recognitionRef.current) {
      if (isListening) {
        recognitionRef.current.stop();
      } else {
        recognitionRef.current.start();
        setIsListening(true);
      }
    }
  };

  const handleQuickSearch = (searchQuery: string) => {
    setQuery(searchQuery);
    onSearch(searchQuery);
    setShowSuggestions(false);
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Main Search Bar */}
      <form onSubmit={handleSubmit} className="relative">
        <div className={`
          relative flex items-center gap-3 p-2 pl-6 
          glass rounded-2xl
          transition-all duration-300
          ${showSuggestions ? 'rounded-b-none border-b-0' : ''}
          focus-within:ring-2 focus-within:ring-[#00D9A5]/50
        `}>
          {/* Search Icon */}
          <svg 
            className="w-6 h-6 text-gray-400" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>

          {/* Input */}
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Search for products... (milk, bread, chips)"
            className="flex-1 bg-transparent text-lg outline-none placeholder-gray-500"
            autoComplete="off"
          />

          {/* Clear Button */}
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                inputRef.current?.focus();
              }}
              className="p-2 hover:bg-white/10 rounded-full transition-colors"
            >
              <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}

          {/* Voice Search */}
          {voiceSupported && (
            <button
              type="button"
              onClick={handleVoiceSearch}
              className={`
                p-3 rounded-xl transition-all
                ${isListening 
                  ? 'bg-[#FF6B6B] text-white animate-pulse' 
                  : 'bg-white/5 hover:bg-white/10 text-gray-400'
                }
              `}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </button>
          )}

          {/* Search Button */}
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className={`
              px-6 py-3 rounded-xl font-semibold text-sm
              transition-all flex items-center gap-2
              ${loading 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'btn-primary'
              }
            `}
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Searching...
              </>
            ) : (
              <>
                Search
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </>
            )}
          </button>
        </div>

        {/* Suggestions Dropdown */}
        {showSuggestions && (
          <div className="absolute top-full left-0 right-0 glass rounded-b-2xl border-t-0 p-4 z-50">
            {/* Popular Searches */}
            <div className="mb-4">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-3">Popular Searches</div>
              <div className="flex flex-wrap gap-2">
                {POPULAR_SEARCHES.map((term) => (
                  <button
                    key={term}
                    type="button"
                    onClick={() => handleQuickSearch(term)}
                    className="px-3 py-1.5 bg-white/5 hover:bg-[#00D9A5]/20 hover:text-[#00D9A5] rounded-full text-sm transition-all"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </form>

      {/* Quick Category Pills */}
      <div className="flex items-center justify-center gap-3 mt-6 flex-wrap">
        <span className="text-sm text-gray-500">Quick:</span>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.label}
            onClick={() => handleQuickSearch(cat.query)}
            className="flex items-center gap-2 px-4 py-2 glass rounded-full hover:bg-white/10 transition-all group"
          >
            <span className="text-lg group-hover:scale-125 transition-transform">{cat.icon}</span>
            <span className="text-sm text-gray-300">{cat.label}</span>
          </button>
        ))}
      </div>

      {/* Voice Search Status */}
      {isListening && (
        <div className="mt-4 text-center">
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-[#FF6B6B]/20 border border-[#FF6B6B]/30 rounded-full">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-[#FF6B6B] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-[#FF6B6B] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-[#FF6B6B] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
            <span className="text-[#FF6B6B] font-medium">Listening...</span>
          </div>
        </div>
      )}
    </div>
  );
}
