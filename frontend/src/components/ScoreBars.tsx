interface ScoreBarsProps {
  originality: number | null
  timing: number | null
  cleverness: number | null
}

export function ScoreBars({ originality, timing, cleverness }: ScoreBarsProps) {
  if (!originality && !timing && !cleverness) return null

  const scores = [
    { label: 'Originality', value: originality, color: 'bg-gold-400' },
    { label: 'Timing', value: timing, color: 'bg-orange-400' },
    { label: 'Cleverness', value: cleverness, color: 'bg-amber-400' },
  ]

  return (
    <div className="space-y-3 pt-4 border-t border-zinc-800">
      {scores.map(({ label, value, color }) => (
        value && (
          <div key={label} className="flex items-center gap-3">
            <span className="text-xs text-zinc-400 w-24 font-medium">{label}</span>
            <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className={`h-full ${color} transition-all duration-500 rounded-full`}
                style={{ width: `${value * 10}%` }}
              />
            </div>
            <span className="text-sm text-white font-semibold w-8 text-right">{value}</span>
          </div>
        )
      ))}
    </div>
  )
}
