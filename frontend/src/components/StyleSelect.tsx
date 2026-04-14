interface StyleSelectProps {
  value: string
  onChange: (style: string) => void
}

const STYLES = [
  { value: 'witty', label: '🎭 Witty' },
  { value: 'dad', label: '👨 Dad' },
  { value: 'sarcastic', label: '😏 Sarcastic' },
  { value: 'roast', label: '🔥 Roast' },
  { value: 'haiku', label: '🌸 Haiku' },
  { value: 'brainrot', label: '🧠 Brainrot' },
  { value: 'nocontext', label: '❓ No Context' },
  { value: 'emoji', label: '😂 Emoji' },
]

export function StyleSelect({ value, onChange }: StyleSelectProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="h-10 px-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
    >
      {STYLES.map((style) => (
        <option key={style.value} value={style.value}>
          {style.label}
        </option>
      ))}
    </select>
  )
}
