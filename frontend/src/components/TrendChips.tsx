interface TrendChipsProps {
  onSelect: (topic: string) => void
}

const TRENDS = [
  'Marriage', 'Work Life', 'Dating Apps', 'Tech Bros', 'Airports',
  'Social Media', 'Parenting', 'Fitness', 'Food Delivery', 'Remote Work',
  'Gaming', 'Streaming', 'Crypto', 'AI', 'Climate Change',
  'Gen Z', 'Millennials', 'Boomers', 'Influencers', 'NFTs',
  'Electric Cars', 'Space Travel', 'Metaverse', 'TikTok', 'LinkedIn'
]

export function TrendChips({ onSelect }: TrendChipsProps) {
  return (
    <div className="relative">
      {/* Gradient fade effects */}
      <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-zinc-950 to-transparent z-10 pointer-events-none"></div>
      <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-zinc-950 to-transparent z-10 pointer-events-none"></div>
      
      {/* Scrollable container */}
      <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1 px-2">
        <div className="flex gap-2 animate-scroll">
          {TRENDS.map((topic) => (
            <button
              key={topic}
              onClick={() => onSelect(topic)}
              className="px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm rounded-full bg-zinc-800/50 border border-zinc-700 text-zinc-300 hover:bg-zinc-700 hover:border-zinc-600 hover:text-white transition-all whitespace-nowrap flex-shrink-0 hover:scale-105"
            >
              {topic}
            </button>
          ))}
          {/* Duplicate for seamless loop */}
          {TRENDS.map((topic) => (
            <button
              key={`${topic}-duplicate`}
              onClick={() => onSelect(topic)}
              className="px-3 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm rounded-full bg-zinc-800/50 border border-zinc-700 text-zinc-300 hover:bg-zinc-700 hover:border-zinc-600 hover:text-white transition-all whitespace-nowrap flex-shrink-0 hover:scale-105"
            >
              {topic}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
