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
      <Card className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-2xl transition-all hover:-translate-y-1">
        <CardContent className="p-4">
          <div className="flex items-start justify-between gap-2 mb-3">
            <h3 className="text-sm font-medium text-zinc-500 dark:text-zinc-400">{joke.query}</h3>
            {onDelete && (
              <button
                onClick={() => onDelete(joke.id)}
                className="text-zinc-300 hover:text-zinc-700 dark:hover:text-zinc-200 text-sm leading-none"
                title="Delete"
              >
                ×
              </button>
            )}
          </div>

          <p id={`joke-${joke.id}`} className="text-zinc-900 dark:text-zinc-100 text-base leading-relaxed mb-4">
            {joke.response}
          </p>

          {showActions && (
            <div className="flex items-center gap-2 flex-wrap">
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
