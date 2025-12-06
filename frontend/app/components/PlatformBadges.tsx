'use client';

const PLATFORMS = [
  { 
    id: 'blinkit', 
    name: 'Blinkit', 
    logo: '🟡', 
    color: 'from-yellow-400 to-yellow-500',
    textColor: 'text-black',
    delivery: '10 min'
  },
  { 
    id: 'zepto', 
    name: 'Zepto', 
    logo: '🟣', 
    color: 'from-purple-500 to-purple-600',
    textColor: 'text-white',
    delivery: '10 min'
  },
  { 
    id: 'instamart', 
    name: 'Instamart', 
    logo: '🟠', 
    color: 'from-orange-500 to-orange-600',
    textColor: 'text-white',
    delivery: '15 min'
  },
  { 
    id: 'bigbasket', 
    name: 'BigBasket', 
    logo: '🟢', 
    color: 'from-lime-500 to-lime-600',
    textColor: 'text-black',
    delivery: '30 min'
  },
  { 
    id: 'jiomart', 
    name: 'JioMart', 
    logo: '🔵', 
    color: 'from-blue-500 to-blue-600',
    textColor: 'text-white',
    delivery: '2-4 hrs'
  },
];

export default function PlatformBadges() {
  return (
    <div className="hidden md:flex items-center justify-center gap-3 mb-8">
      {PLATFORMS.map((platform, index) => (
        <div
          key={platform.id}
          className={`
            flex items-center gap-2 px-4 py-2.5 rounded-full
            bg-gradient-to-r ${platform.color}
            ${platform.textColor}
            shadow-lg transform hover:scale-105 transition-all
            cursor-default
          `}
          style={{ animationDelay: `${index * 100}ms` }}
        >
          <span className="text-lg">{platform.logo}</span>
          <span className="font-semibold text-sm">{platform.name}</span>
          <span className="text-xs opacity-80">• {platform.delivery}</span>
        </div>
      ))}
    </div>
  );
}
