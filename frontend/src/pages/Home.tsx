import { useState } from 'react'
import { useJokeStream } from '@/hooks/useJokeStream'
import { useJokeStore } from '@/store/jokeStore'
import { useProfileStore } from '@/store/profileStore'
import { StyleSelect } from '@/components/StyleSelect'
import { TrendChips } from '@/components/TrendChips'
import { triggerConfetti } from '@/lib/confetti'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

export default function Home() {
  const [query, setQuery] = useState('')
  const { currentStyle, setStyle, streamingTokens, clearStream } = useJokeStore()
  const { fetch: fetchProfile } = useProfileStore()

  const { streaming, startStream } = useJokeStream({
    onComplete: (full) => {
      triggerConfetti(currentStyle)
      fetchProfile()
    },
  })

  const handleGenerate = () => {
    if (!query.trim()) return
    clearStream()
    startStream(query.trim(), currentStyle)
  }

  return (
    <div className="space-y-5">
      {/* Search form */}
      <div className="flex gap-2">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
          placeholder="Enter a topic (e.g. Traffic, Cats, AI)"
          maxLength={100}
          className="flex-1 rounded-xl"
        />
        <StyleSelect value={currentStyle} onChange={setStyle} />
        <Button onClick={handleGenerate} disabled={streaming || !query.trim()}>
          {streaming ? 'Generating…' : 'Go'}
        </Button>
      </div>

      {/* Trend chips */}
      <TrendChips onSelect={setQuery} />

      {/* Streaming result */}
      {(streaming || streamingTokens) && (
        <div className="joke-card p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-2xl min-h-[80px]">
          <p className="text-zinc-900 dark:text-zinc-100 leading-relaxed">
            {streamingTokens}
            {streaming && <span className="animate-pulse">▍</span>}
          </p>
        </div>
      )}

      {/* Heckle section */}
      <HeckleBox />
    </div>
  )
}

function HeckleBox() {
  const [input, setInput] = useState('')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    if (!input.trim()) return
    setLoading(true)
    const res = await fetch('/api/heckle', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ joke: input }),
    })
    const data = await res.json()
    setResult(data.roast)
    setLoading(false)
  }

  return (
    <div className="p-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-2xl">
      <h5 className="text-sm font-medium mb-3 text-zinc-700 dark:text-zinc-300">
        Reverse Heckler — tell the AI your joke
      </h5>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        rows={2}
        placeholder="Type your joke here…"
        className="w-full text-sm p-2 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-transparent resize-none focus:outline-none focus:ring-1 focus:ring-violet-500"
      />
      <Button
        onClick={submit}
        disabled={loading || !input.trim()}
        variant="destructive"
        size="sm"
        className="mt-2"
      >
        {loading ? 'Rating…' : 'Rate & Roast'}
      </Button>
      {result && (
        <p className="mt-3 text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed">{result}</p>
      )}
    </div>
  )
}
