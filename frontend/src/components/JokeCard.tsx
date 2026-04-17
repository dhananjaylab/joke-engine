import { Card, CardContent } from '@/components/ui/card'
import { ShareButton } from './ShareButton'
import { AudioPlayer } from './AudioPlayer'
import { ScoreBars } from './ScoreBars'
import { useSwipe } from '@/hooks/useSwipe'
import type { JokeResponse } from '@/api/jokes'

interface JokeCardProps {
  joke: JokeResponse
  onRegenerate?: () => void
  onDelete?: (id: number) => void
  showActions?: boolean
}

export function JokeCard({ joke, onRegenerate, onDelete, showActions = true }: JokeCardProps) {
  const { ref, bind } = useSwipe({
    onSwipeRight: () => navigator.clipboard?.writeText(joke.response),
    onSwipeLeft: () => onRegenerate?.(),
  })

  return (
    <div ref={ref} {...bind()} className="touch-none select-none cursor-grab active:cursor-grabbing">
      <Card className="bg-zinc-900/50 border border-zinc-800 rounded-2xl transition-all hover:border-zinc-700 hover:-translate-y-1">
        <CardContent className="p-6">
          <div className="flex items-start justify-between gap-2 mb-4">
            <div className="flex items-center gap-2">
              <span className="text-xs px-2 py-1 rounded-full bg-gold-400/10 text-gold-400 border border-gold-400/20">
                {joke.style || 'Comedy'}
              </span>
              <h3 className="text-sm font-medium text-zinc-400">{joke.query}</h3>
            </div>
            {onDelete && (
              <button
                onClick={() => onDelete(joke.id)}
                className="text-zinc-500 hover:text-zinc-300 transition-colors"
                title="Delete"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>

          <p id={`joke-${joke.id}`} className="text-white text-lg leading-relaxed mb-6">
            {joke.response}
          </p>

          {showActions && (
            <div className="flex items-center gap-2 flex-wrap mb-4">
              <ShareButton jokeId={joke.id} jokeText={joke.response} />
              <AudioPlayer jokeId={joke.id} />
            </div>
          )}

          <ScoreBars
            originality={joke.score_originality}
            timing={joke.score_timing}
            cleverness={joke.score_cleverness}
          />
        </CardContent>
      </Card>
    </div>
  )
}
