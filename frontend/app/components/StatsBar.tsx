'use client';

interface StatsBarProps {
  platformsCount: number;
  productsCount: number;
  avgSavings: number;
}

export default function StatsBar({ platformsCount, productsCount, avgSavings }: StatsBarProps) {
  const stats = [
    {
      icon: '🏪',
      value: platformsCount,
      label: 'Platforms',
      color: 'from-purple-500 to-purple-600',
      suffix: ''
    },
    {
      icon: '📦',
      value: productsCount.toLocaleString(),
      label: 'Products',
      color: 'from-blue-500 to-blue-600',
      suffix: '+'
    },
    {
      icon: '💰',
      value: avgSavings,
      label: 'Avg. Savings',
      color: 'from-[#00D9A5] to-emerald-600',
      suffix: '%'
    },
    {
      icon: '⚡',
      value: '10',
      label: 'Min Delivery',
      color: 'from-orange-500 to-orange-600',
      suffix: ' min'
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 my-10">
      {stats.map((stat, index) => (
        <div
          key={stat.label}
          className="stat-card flex items-center gap-4 group"
          style={{ animationDelay: `${index * 100}ms` }}
        >
          <div className={`
            w-14 h-14 rounded-2xl bg-gradient-to-br ${stat.color}
            flex items-center justify-center text-2xl
            shadow-lg group-hover:scale-110 transition-transform
          `}>
            {stat.icon}
          </div>
          <div>
            <div className="text-2xl font-bold">
              {stat.value}
              <span className="text-lg text-gray-400">{stat.suffix}</span>
            </div>
            <div className="text-sm text-gray-500">{stat.label}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
