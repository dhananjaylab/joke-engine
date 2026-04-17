interface StyleSelectProps {
  value: string
  onChange: (style: string) => void
}

const STYLES = [
  { value: 'sarcastic', label: 'Sarcastic' },
  { value: 'witty', label: 'Witty' },
  { value: 'dad', label: 'Dad Jokes' },
  { value: 'roast', label: 'Roast' },
  { value: 'observational', label: 'Observational' },
  { value: 'dark', label: 'Dark' },
]

export function StyleSelect({ value, onChange }: StyleSelectProps) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-12 px-4 pr-10 rounded-xl border border-zinc-700 bg-zinc-900 text-white appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-gold-400/50 transition-all"
      >
        {STYLES.map((style) => (
          <option key={style.value} value={style.value}>
            {style.label}
          </option>
        ))}
      </select>
      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg className="w-5 h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  )
}
