import confetti from 'canvas-confetti'

export function triggerConfetti(style: string) {
  const colors = {
    witty: ['#a855f7', '#ec4899', '#f59e0b'],
    dad: ['#fbbf24', '#fb923c', '#f87171'],
    sarcastic: ['#6366f1', '#8b5cf6', '#a855f7'],
    roast: ['#ef4444', '#f97316', '#dc2626'],
    haiku: ['#10b981', '#14b8a6', '#06b6d4'],
    brainrot: ['#ff00ff', '#00ffff', '#ffff00'],
    default: ['#a855f7', '#ec4899', '#f59e0b'],
  }

  const colorSet = colors[style as keyof typeof colors] || colors.default

  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
    colors: colorSet,
  })
}
