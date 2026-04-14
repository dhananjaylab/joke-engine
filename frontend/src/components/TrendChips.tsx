interface TrendChipsProps {
  onSelect: (topic: string) => void
}

const TRENDS = ['AI', 'Traffic', 'Cats', 'Coffee', 'Monday', 'Weather']

export function TrendChips({ onSelect }: TrendChipsProps) {
  return (
    <div className="flex gap-2 flex-wrap">
      {TRENDS.map((topic) => (
        <button
          key={topic}
          onClick={() => onSelect(topic)}
          className="px-3 py-1 text-xs rounded-full bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 hover:bg-violet-200 dark:hover:bg-violet-900/50 transition-colors"
        >
          {topic}
        </button>
      ))}
    </div>
  )
}
