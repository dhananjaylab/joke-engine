interface LengthSelectProps {
  value: string
  onChange: (length: string) => void
}

const LENGTHS = [
  { value: 'one-liner', label: '⚡', title: 'One-liner' },
  { value: 'short', label: '📝', title: 'Short' },
  { value: 'medium', label: '📄', title: 'Medium' },
  { value: 'long', label: '📚', title: 'Long' },
  { value: 'epic', label: '🎭', title: 'Epic' },
]

export function LengthSelect({ value, onChange }: LengthSelectProps) {
  return (
    <div>
      <label className="block text-xs text-zinc-500 mb-2 uppercase tracking-wide">Length</label>
      <div className="flex gap-1">
        {LENGTHS.map((length) => (
          <button
            key={length.value}
            onClick={() => onChange(length.value)}
            className={`flex-1 h-11 sm:h-12 rounded-xl text-lg font-medium transition-all border ${
              value === length.value
                ? 'bg-gold-400/20 border-gold-400/50 text-gold-400'
                : 'bg-zinc-800/50 border-zinc-700 text-zinc-300 hover:bg-zinc-700 hover:border-zinc-600 hover:text-white'
            }`}
            title={length.title}
          >
            {length.label}
          </button>
        ))}
      </div>
    </div>
  )
}