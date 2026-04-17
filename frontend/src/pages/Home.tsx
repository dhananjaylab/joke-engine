import { useState } from 'react'
import { useJokeStream } from '@/hooks/useJokeStream'
import { useJokeWebSocket } from '@/hooks/useJokeWebSocket'
import { useJokeStore } from '@/store/jokeStore'
import { useProfileStore } from '@/store/profileStore'
import { StyleSelect } from '@/components/StyleSelect'
import { TrendChips } from '@/components/TrendChips'
import { triggerConfetti } from '@/lib/confetti'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

export default function Home() {
  const [query, setQuery] = useState('')
  const [useWebSocket, setUseWebSocket] = useState(false)
  const { currentStyle, setStyle, streamingTokens, clearStream } = useJokeStore()
  const { fetch: fetchProfile } = useProfileStore()

  const sseStream = useJokeStream({
    onComplete: (full) => {
      triggerConfetti(currentStyle)
      fetchProfile()
    },
  })

  const wsStream = useJokeWebSocket({
    onComplete: (full) => {
      triggerConfetti(currentStyle)
      fetchProfile()
    },
  })

  const currentStream = useWebSocket ? wsStream : sseStream

  const handleGenerate = () => {
    if (!query.trim()) return
    clearStream()
    currentStream.startStream(query.trim(), currentStyle)
  }

  return (
    <div className="space-y-6 sm:space-y-8 max-w-3xl mx-auto">
      {/* Status Badges */}
      <div className="flex items-center justify-center gap-2 sm:gap-3 text-xs sm:text-sm flex-wrap">
        <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full bg-zinc-800/50 border border-zinc-700">
          <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-zinc-300 text-[10px] sm:text-xs">LIVE AI ENGINE ACTIVE</span>
        </div>
        <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full bg-zinc-800/50 border border-zinc-700">
          <span className="text-zinc-400 text-[10px] sm:text-xs">SSE/WEBSOCKET</span>
        </div>
      </div>

      {/* Hero Section */}
      <div className="text-center space-y-3 sm:space-y-4 px-4 sm:px-0">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight leading-tight">
          <span className="text-white">GENERATE</span>
          <span className="text-gold-400">COMEDY</span>
        </h1>
        <p className="text-zinc-400 text-sm sm:text-base md:text-lg">
          Choose a topic and style. Watch AI write in real-time.
        </p>
      </div>

      {/* Generation Form */}
      <div className="space-y-3 sm:space-y-4">
        <div className="flex flex-col gap-3">
          <div className="flex-1">
            <label className="block text-xs text-zinc-500 mb-2 uppercase tracking-wide">Topic</label>
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
              placeholder="e.g., Working from home"
              maxLength={100}
              className="bg-zinc-900 border-zinc-700 text-white placeholder:text-zinc-500 h-11 sm:h-12 rounded-xl text-sm sm:text-base"
            />
          </div>
          <div className="w-full sm:w-auto">
            <label className="block text-xs text-zinc-500 mb-2 uppercase tracking-wide">Style</label>
            <StyleSelect value={currentStyle} onChange={setStyle} />
          </div>
        </div>

        <Button 
          onClick={handleGenerate} 
          disabled={currentStream.streaming || !query.trim()}
          className="w-full h-12 sm:h-14 bg-gold-400 hover:bg-gold-500 text-black font-bold text-base sm:text-lg rounded-xl transition-all hover:shadow-lg hover:shadow-gold-400/20 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {currentStream.streaming ? (
            <>
              <span className="animate-pulse">Generating...</span>
            </>
          ) : (
            <>
              GENERATE ⚡
            </>
          )}
        </Button>
      </div>

      {/* Trending Topics */}
      <div className="space-y-2 sm:space-y-3">
        <div className="text-xs sm:text-sm text-zinc-500 uppercase tracking-wide text-center sm:text-left">Trending:</div>
        <TrendChips onSelect={setQuery} />
      </div>

      {/* Streaming Result */}
      {(currentStream.streaming || streamingTokens) && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-4 sm:p-6 min-h-[100px] sm:min-h-[120px]">
          <p className="text-white text-base sm:text-lg leading-relaxed">
            {streamingTokens}
            {currentStream.streaming && <span className="animate-pulse ml-1">▍</span>}
          </p>
        </div>
      )}

      {/* Two Column Layout - Stack on Mobile */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 mt-8 sm:mt-12">
        {/* Reverse Heckler */}
        <HeckleBox />

        {/* Top Rated */}
        <TopRatedBox />
      </div>
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
    try {
      const res = await fetch('/api/heckle', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ joke: input }),
      })
      const data = await res.json()
      setResult(data.roast)
    } catch (error) {
      console.error('Heckle error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-4 sm:p-6 space-y-3 sm:space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-xl sm:text-2xl">🎤</span>
        <h3 className="text-base sm:text-lg font-bold text-white">Reverse Heckler</h3>
      </div>
      <p className="text-xs sm:text-sm text-zinc-400">
        Think you're funny? Submit your joke for a professional roast.
      </p>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        rows={3}
        placeholder="Type your best joke here..."
        className="w-full bg-zinc-800/50 border border-zinc-700 text-white placeholder:text-zinc-500 rounded-xl p-3 resize-none focus:outline-none focus:ring-2 focus:ring-gold-400/50 text-sm sm:text-base"
      />
      <Button
        onClick={submit}
        disabled={loading || !input.trim()}
        className="w-full bg-gold-400 hover:bg-gold-500 text-black font-semibold rounded-xl h-10 sm:h-11 text-sm sm:text-base"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="animate-spin">⚡</span>
            Rating...
          </span>
        ) : (
          <>🔥 GET ROASTED</>
        )}
      </Button>
      {result && (
        <div className="mt-3 sm:mt-4 p-3 sm:p-4 bg-zinc-800/50 rounded-xl border border-zinc-700">
          <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">{result}</p>
        </div>
      )}
    </div>
  )
}

function TopRatedBox() {
  return (
    <div className="bg-gradient-to-br from-zinc-900 to-zinc-900/50 border border-zinc-800 rounded-2xl p-4 sm:p-6 space-y-3 sm:space-y-4 relative overflow-hidden">
      {/* Microphone Icon */}
      <div className="flex justify-center mb-3 sm:mb-4">
        <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-br from-gold-400/20 to-gold-600/20 flex items-center justify-center">
          <svg className="w-10 h-10 sm:w-12 sm:h-12 text-gold-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </div>
      </div>

      <div className="space-y-1.5 sm:space-y-2">
        <div className="text-[10px] sm:text-xs text-gold-400 font-semibold uppercase tracking-wide">Top Rated</div>
        <h3 className="text-lg sm:text-xl font-bold text-white">The AI Standup Special</h3>
        <p className="text-xs sm:text-sm text-zinc-400">
          Watch the highest-rated generated sets of the week, curated globally.
        </p>
      </div>

      <button className="flex items-center gap-2 text-gold-400 hover:text-gold-300 font-semibold transition-colors group text-sm sm:text-base">
        <span>Watch Now</span>
        <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  )
}
