'use client';

import { useState, useRef, useEffect, useCallback } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

// Supported languages for voice input
const LANGUAGES = [
  { code: 'en-IN', name: 'English', flag: '🇮🇳' },
  { code: 'hi-IN', name: 'हिंदी', flag: '🇮🇳' },
  { code: 'ta-IN', name: 'தமிழ்', flag: '🇮🇳' },
  { code: 'te-IN', name: 'తెలుగు', flag: '🇮🇳' },
  { code: 'mr-IN', name: 'मराठी', flag: '🇮🇳' },
  { code: 'bn-IN', name: 'বাংলা', flag: '🇮🇳' },
  { code: 'gu-IN', name: 'ગુજરાતી', flag: '🇮🇳' },
  { code: 'kn-IN', name: 'ಕನ್ನಡ', flag: '🇮🇳' },
  { code: 'ml-IN', name: 'മലയാളം', flag: '🇮🇳' },
  { code: 'pa-IN', name: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
];

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  action?: string;
  data?: Record<string, unknown>;
  suggestions?: string[];
  isVoice?: boolean;
}

interface ChatbotProps {
  onSearch?: (query: string) => void;
  onShowDeals?: () => void;
  onQuickOrder?: (query: string) => void;
  onBuyNow?: (query: string) => void;
  onOneClickCheckout?: (query: string) => void;
  onNegotiate?: (query: string) => void;
  onOpenBuyerDashboard?: (tab?: string) => void;
  onOpenSellerDashboard?: () => void;
  onOpenAdminDashboard?: () => void;
}

// Use any for Web Speech API to avoid TypeScript conflicts
/* eslint-disable @typescript-eslint/no-explicit-any */

export default function Chatbot({ onSearch, onShowDeals, onQuickOrder, onBuyNow, onOneClickCheckout, onNegotiate, onOpenBuyerDashboard, onOpenSellerDashboard, onOpenAdminDashboard }: ChatbotProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  
  // Voice states
  const [isListening, setIsListening] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('en-IN');
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognitionAPI) {
        const recognition = new SpeechRecognitionAPI();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = selectedLanguage;

        recognition.onstart = () => {
          setIsListening(true);
          setInterimTranscript('');
        };

        recognition.onresult = (event: any) => {
          let finalTranscript = '';
          let interimText = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimText += transcript;
            }
          }

          setInterimTranscript(interimText);

          if (finalTranscript) {
            setInput(finalTranscript);
            setInterimTranscript('');
            // Auto-send after voice input
            setTimeout(() => {
              sendMessage(finalTranscript, true);
            }, 300);
          }
        };

        recognition.onerror = (event: any) => {
          console.error('Speech recognition error:', event);
          setIsListening(false);
          setInterimTranscript('');
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current = recognition;
      }
    }
  }, [selectedLanguage]);

  // Update recognition language when changed
  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = selectedLanguage;
    }
  }, [selectedLanguage]);

  // Add initial greeting when first opened
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: "👋 Hi! I'm your **Price Comparison Assistant**!\n\n" +
                "🎤 **Voice enabled!** Click the mic to speak.\n\n" +
                "**What I can do:**\n" +
                "🔍 \"Find Amul milk\" - Search products\n" +
                "⚡ \"One-click buy bread\" - Fast checkout\n" +
                "🛒 \"Quick order Maggi\" - Quick order\n" +
                "💰 \"Cheapest eggs\" - Find lowest price\n" +
                "🔥 \"Show deals\" - Today's offers\n\n" +
                "What would you like? 🛒",
        timestamp: new Date().toISOString(),
        suggestions: ['⚡ One-click buy milk', '🛒 Quick order Maggi', 'Show deals', '🎤 Speak']
      }]);
    }
  }, [isOpen, messages.length]);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Voice recognition is not supported in your browser. Try Chrome or Edge.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.start();
      } catch (error) {
        console.error('Error starting recognition:', error);
      }
    }
  };

  const sendMessage = async (messageText: string, isVoice = false) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
      isVoice
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText })
      });

      if (!response.ok) throw new Error('Chat failed');

      const data = await response.json();

      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp,
        action: data.action,
        data: data.data,
        suggestions: data.suggestions
      };

      setMessages(prev => [...prev, botMessage]);

      // Handle actions
      if (data.action === 'search' && data.data?.query && onSearch) {
        setTimeout(() => onSearch(data.data.query as string), 500);
      } else if (data.action === 'deals' && onShowDeals) {
        setTimeout(() => onShowDeals(), 500);
      } else if (data.action === 'one_click_checkout' && data.data?.query && onOneClickCheckout) {
        setTimeout(() => onOneClickCheckout(data.data.query as string), 500);
      } else if (data.action === 'buy_now' && data.data?.query && onBuyNow) {
        setTimeout(() => onBuyNow(data.data.query as string), 500);
      } else if (data.action === 'quick_order' && data.data?.query && onQuickOrder) {
        setTimeout(() => onQuickOrder(data.data.query as string), 500);
      } else if (data.action === 'negotiate' && data.data?.query && onNegotiate) {
        setTimeout(() => onNegotiate(data.data.query as string), 500);
      } else if (data.action === 'open_buyer_dashboard') {
        if (onOpenBuyerDashboard) {
          setTimeout(() => onOpenBuyerDashboard(data.data?.tab as string), 500);
        } else {
          // Fallback: open in new window
          window.open(`/buyer${data.data?.tab ? `?tab=${data.data.tab}` : ''}`, '_blank');
        }
      } else if (data.action === 'open_seller_dashboard') {
        if (onOpenSellerDashboard) {
          setTimeout(() => onOpenSellerDashboard(), 500);
        } else {
          window.open('/seller', '_blank');
        }
      } else if (data.action === 'open_admin_dashboard') {
        if (onOpenAdminDashboard) {
          setTimeout(() => onOpenAdminDashboard(), 500);
        } else {
          window.open('/admin', '_blank');
        }
      }

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: '😔 Sorry, I encountered an error. Please try again!',
        timestamp: new Date().toISOString(),
        suggestions: ['Try again', 'Search milk', 'Show deals']
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (suggestion === '🎤 Speak') {
      toggleListening();
    } else {
      sendMessage(suggestion);
    }
  };

  // Format message content with markdown-like styling
  const formatContent = (content: string) => {
    return content
      .split('\n')
      .map((line) => {
        // Bold text
        line = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        return line;
      })
      .join('<br />');
  };

  const currentLang = LANGUAGES.find(l => l.code === selectedLanguage) || LANGUAGES[0];

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-br from-primary to-purple-600 rounded-full shadow-2xl flex items-center justify-center text-3xl hover:scale-110 transition-transform z-50 animate-bounce"
        title="Chat with AI Assistant"
      >
        💬
      </button>
    );
  }

  return (
    <div 
      className={`fixed bottom-6 right-6 z-50 flex flex-col transition-all duration-300 ${
        isMinimized ? 'w-72 h-14' : 'w-96 h-[600px] max-h-[80vh]'
      }`}
    >
      {/* Chat Window */}
      <div className="glass rounded-2xl shadow-2xl flex flex-col h-full overflow-hidden border border-primary/30">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary/20 to-purple-600/20 p-4 flex items-center justify-between border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xl ${
              isListening ? 'bg-red-500/30 animate-pulse' : 'bg-primary/30'
            }`}>
              {isListening ? '🎤' : '🤖'}
            </div>
            <div>
              <h3 className="font-bold text-sm">Price Assistant</h3>
              <p className="text-xs text-gray-400">
                {isListening ? `🔴 Listening in ${currentLang.name}...` : 'Voice enabled 🎤'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title={isMinimized ? 'Expand' : 'Minimize'}
            >
              {isMinimized ? '⬆️' : '⬇️'}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Close"
            >
              ✕
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                    {/* Message Bubble */}
                    <div
                      className={`rounded-2xl px-4 py-3 ${
                        msg.role === 'user'
                          ? 'bg-primary text-white rounded-br-none'
                          : 'bg-white/10 rounded-bl-none'
                      }`}
                    >
                      {msg.role === 'user' && msg.isVoice && (
                        <span className="text-xs opacity-70 mr-1">🎤</span>
                      )}
                      <div 
                        className="text-sm whitespace-pre-wrap inline"
                        dangerouslySetInnerHTML={{ __html: formatContent(msg.content) }}
                      />
                    </div>

                    {/* Suggestions */}
                    {msg.role === 'assistant' && msg.suggestions && msg.suggestions.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {msg.suggestions.map((suggestion, i) => (
                          <button
                            key={i}
                            onClick={() => handleSuggestionClick(suggestion)}
                            className={`text-xs px-3 py-1.5 border rounded-full transition-colors ${
                              suggestion === '🎤 Speak' 
                                ? 'bg-red-500/20 border-red-500/30 hover:bg-red-500/30' 
                                : 'bg-white/5 border-white/10 hover:bg-white/10'
                            }`}
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Timestamp */}
                    <p className="text-[10px] text-gray-500 mt-1 px-1">
                      {new Date(msg.timestamp).toLocaleTimeString('en-IN', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              ))}

              {/* Interim transcript */}
              {interimTranscript && (
                <div className="flex justify-end">
                  <div className="bg-primary/50 text-white rounded-2xl rounded-br-none px-4 py-3 max-w-[85%]">
                    <span className="text-xs opacity-70 mr-1">🎤</span>
                    <span className="text-sm italic">{interimTranscript}...</span>
                  </div>
                </div>
              )}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white/10 rounded-2xl rounded-bl-none px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input with Voice */}
            <form onSubmit={handleSubmit} className="p-4 border-t border-white/10">
              {/* Language Selector (shown when clicking flag) */}
              {showLanguageSelector && (
                <div className="absolute bottom-20 left-4 right-4 bg-slate-800 rounded-xl border border-white/10 shadow-xl p-2 max-h-48 overflow-y-auto">
                  <p className="text-xs text-gray-400 px-2 py-1">Select language:</p>
                  {LANGUAGES.map((lang) => (
                    <button
                      key={lang.code}
                      type="button"
                      onClick={() => {
                        setSelectedLanguage(lang.code);
                        setShowLanguageSelector(false);
                      }}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm flex items-center gap-2 ${
                        selectedLanguage === lang.code 
                          ? 'bg-primary/20 text-primary' 
                          : 'hover:bg-white/10'
                      }`}
                    >
                      <span>{lang.flag}</span>
                      <span>{lang.name}</span>
                      {selectedLanguage === lang.code && <span className="ml-auto">✓</span>}
                    </button>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                {/* Language button */}
                <button
                  type="button"
                  onClick={() => setShowLanguageSelector(!showLanguageSelector)}
                  className="px-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-colors text-lg"
                  title={`Language: ${currentLang.name}`}
                >
                  {currentLang.flag}
                </button>

                {/* Voice button */}
                <button
                  type="button"
                  onClick={toggleListening}
                  disabled={isLoading}
                  className={`px-4 rounded-xl transition-all flex items-center justify-center ${
                    isListening
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                      : 'bg-white/10 hover:bg-white/20 border border-white/10'
                  }`}
                  title={isListening ? 'Stop listening' : 'Start voice input'}
                >
                  {isListening ? (
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-white rounded-full animate-ping" />
                      🎤
                    </span>
                  ) : (
                    '🎤'
                  )}
                </button>

                {/* Text input */}
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={isListening ? "Listening..." : "Type or speak..."}
                  className={`flex-1 bg-white/5 border rounded-xl px-4 py-3 text-sm focus:outline-none transition-colors ${
                    isListening 
                      ? 'border-red-500/50 bg-red-500/5' 
                      : 'border-white/10 focus:border-primary/50'
                  }`}
                  disabled={isLoading || isListening}
                />

                {/* Send button */}
                <button
                  type="submit"
                  disabled={isLoading || !input.trim() || isListening}
                  className="px-4 bg-primary hover:bg-primary/80 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-xl transition-colors"
                >
                  {isLoading ? '...' : '➤'}
                </button>
              </div>

              {/* Voice status */}
              {isListening && (
                <div className="mt-2 flex items-center justify-center gap-2 text-sm text-red-400">
                  <span className="flex gap-1">
                    <span className="w-1 h-3 bg-red-400 rounded animate-pulse" style={{ animationDelay: '0ms' }} />
                    <span className="w-1 h-4 bg-red-400 rounded animate-pulse" style={{ animationDelay: '100ms' }} />
                    <span className="w-1 h-2 bg-red-400 rounded animate-pulse" style={{ animationDelay: '200ms' }} />
                    <span className="w-1 h-5 bg-red-400 rounded animate-pulse" style={{ animationDelay: '300ms' }} />
                    <span className="w-1 h-3 bg-red-400 rounded animate-pulse" style={{ animationDelay: '400ms' }} />
                  </span>
                  <span>Speak now in {currentLang.name}...</span>
                </div>
              )}

              {!isListening && (
                <p className="text-[10px] text-gray-500 mt-2 text-center">
                  🎤 Click mic to speak • 10 Indian languages supported
                </p>
              )}
            </form>
          </>
        )}
      </div>
    </div>
  );
}
