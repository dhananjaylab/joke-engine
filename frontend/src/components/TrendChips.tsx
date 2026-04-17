interface TrendChipsProps {
  onSelect: (topic: string) => void
}

const TRENDS = ['Marriage', 'Work Life', 'Dating Apps', 'Tech Bros', 'Airports']

export function TrendChips({ onSelect }: TrendChipsProps) {
  return (
    <div className="flex gap-2 flex-wrap justify-center">
      {TRENDS.map((topic) => (
        <button
          key={topic}
          onClick={() => onSelect(topic)}
          className="px-4 py-2 text-sm rounded-full bg-zinc-800/50 border border-zinc-700 text-zinc-300 hover:bg-zinc-700 hover:border-zinc-600 hover:text-white transition-all"
        >
          {topic}
        </button>
      ))}
    </div>
  )
}
