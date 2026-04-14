interface ScoreBarsProps {
  originality: number | null
  timing: number | null
  cleverness: number | null
}

export function ScoreBars({ originality, timing, cleverness }: ScoreBarsProps) {
  if (!originality && !timing && !cleverness) return null

  const scores = [
    { label: 'Originality', value: originality, color: 'bg-blue-500' },
    { label: 'Timing', value: timing, color: 'bg-green-500' },
    { label: 'Cleverness', value: cleverness, color: 'bg-purple-500' },
  ]

  return (
    <div className="mt-4 space-y-2">
      {scores.map(({ label, value, color }) => (
        value && (
          <div key={label} className="flex items-center gap-2">
            <span className="text-xs text-zinc-500 dark:text-zinc-400 w-20">{label}</span>
            <div className="flex-1 h-2 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
              <div
                className={`h-full ${color} transition-all duration-500`}
                style={{ width: `${value * 10}%` }}
              />
            </div>
            <span className="text-xs text-zinc-600 dark:text-zinc-300 w-6">{value}</span>
          </div>
        )
      ))}
    </div>
  )
}
