import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useJokeStream } from '@/hooks/useJokeStream'
import { useJokeStore } from '@/store/jokeStore'
import { useProfileStore } from '@/store/profileStore'
import { StyleSelect } from '@/components/StyleSelect'
import { TrendChips } from '@/components/TrendChips'
import { triggerConfetti } from '@/lib/confetti'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { jokeApi } from '@/api/jokes'
import type { JokeResponse } from '@/api/jokes'

export default function Home() {
  const location = useLocation()
  const [query, setQuery] = useState('')
  const [jokeOfTheDay, setJokeOfTheDay] = useState<string | null>(null)
  const [jotdLoading, setJotdLoading] = useState(true)
  const { currentStyle, setStyle, streamingTokens, clearStream, setJoke } = useJokeStore()
  const { fetch: fetchProfile } = useProfileStore()

  // Handle navigation state (from navbar search)
  useEffect(() => {
    if (location.state?.query) {
      setQuery(location.state.query)
      if (location.state.style) {
        setStyle(location.state.style)
      }
      // Auto-generate if query was passed
      setTimeout(() => {
        handleGenerate(location.state.query, location.state.style || currentStyle)
      }, 100)
      // Clear the state
      globalThis.history.replaceState({}, document.title)
    }
  }, [location.state, currentStyle, setStyle])

  // Fetch joke of the day on mount
  useEffect(() => {
    const fetchJokeOfTheDay = async () => {
      try {
        const data = await jokeApi.jokeOfTheDay()
        setJokeOfTheDay(data.joke)
      } catch (error: any) {
        console.error('Failed to fetch joke of the day:', error)
      } finally {
        setJotdLoading(false)
      }
    }
    fetchJokeOfTheDay()
  }, [])

  const sseStream = useJokeStream({
    onComplete: (joke, id) => {
      triggerConfetti(currentStyle)
      fetchProfile()
      if (id) {
        setJoke(joke, id)
      }
    },
  })

  const currentStream = sseStream

  const handleGenerate = (queryText?: string, styleText?: string) => {
    const finalQuery = queryText || query.trim()
    const finalStyle = styleText || currentStyle
    
    if (!finalQuery) return
    clearStream()
    currentStream.startStream(finalQuery, finalStyle)
  }

  return (
    <div className="space-y-6 sm:space-y-8 max-w-3xl mx-auto">
      {/* Joke of the Day Banner */}
      {jokeOfTheDay && (
        <div className="bg-gradient-to-r from-gold-400/10 via-gold-500/10 to-gold-400/10 border border-gold-400/30 rounded-2xl p-4 sm:p-6 relative overflow-hidden animate-in fade-in slide-in-from-top-4 duration-700">
          {/* Animated background elements */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-gold-400/5 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-gold-500/5 rounded-full blur-2xl animate-pulse delay-300"></div>
          
          {/* Sparkle effects */}
          <div className="absolute top-4 right-8 text-gold-400/30 animate-bounce delay-100">✨</div>
          <div className="absolute top-8 right-16 text-gold-400/20 animate-bounce delay-300">⭐</div>
          <div className="absolute bottom-6 left-8 text-gold-400/25 animate-bounce delay-500">💫</div>
          
          <div className="relative">
            <div className="flex items-center gap-2 mb-3 animate-in fade-in slide-in-from-left duration-500">
              <span className="text-2xl animate-bounce">🌟</span>
              <h2 className="text-lg sm:text-xl font-bold text-gold-400 tracking-wide">
                Joke of the Day
              </h2>
            </div>
            <p className="text-white text-base sm:text-lg leading-relaxed animate-in fade-in slide-in-from-bottom duration-700 delay-200">
              {jokeOfTheDay}
            </p>
          </div>
        </div>
      )}

      {jotdLoading && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-4 sm:p-6 animate-pulse">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 bg-zinc-800 rounded"></div>
            <div className="h-6 w-40 bg-zinc-800 rounded"></div>
          </div>
          <div className="space-y-2">
            <div className="h-4 bg-zinc-800 rounded w-full"></div>
            <div className="h-4 bg-zinc-800 rounded w-3/4"></div>
          </div>
        </div>
      )}

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
          onClick={() => handleGenerate()} 
          disabled={currentStream.streaming || !query.trim()}
          className="w-full h-12 sm:h-14 bg-gold-400 hover:bg-gold-500 text-black font-bold text-base sm:text-lg rounded-xl transition-all hover:shadow-lg hover:shadow-gold-400/20 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {currentStream.streaming ? (
            <span className="animate-pulse">Generating...</span>
          ) : (
            'GENERATE ⚡'
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

        {/* Random Jokes */}
        <RandomJokesBox />
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
            {' '}Rating...
          </span>
        ) : (
          '🔥 GET ROASTED'
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

function RandomJokesBox() {
  const [joke, setJoke] = useState<JokeResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [flipped, setFlipped] = useState(false)

  const fetchJoke = async () => {
    setLoading(true)
    setFlipped(false)
    try {
      const data = await jokeApi.randomJokes()
      setJoke(data)
    } catch (error) {
      console.error('Random joke error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNext = async () => {
    setFlipped(true)
    setTimeout(async () => {
      setFlipped(false)
      await fetchJoke()
    }, 200)
  }

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-4 sm:p-6 space-y-3 sm:space-y-4 flex flex-col">
      <div className="flex items-center gap-2">
        <span className="text-xl sm:text-2xl">🎲</span>
        <h3 className="text-base sm:text-lg font-bold text-white">Random Joke</h3>
      </div>

      <p className="text-xs sm:text-sm text-zinc-400">
        Pull a fresh joke from our curated collection — no AI, just pure human comedy.
      </p>

      {/* Joke display */}
      <div className="flex-1 min-h-[80px] flex items-center">
        {!joke && !loading && (
          <p className="text-zinc-500 text-sm italic">Hit the button to get a random joke ↓</p>
        )}
        {loading && (
          <div className="w-full space-y-2 animate-pulse">
            <div className="h-3 bg-zinc-800 rounded w-full"></div>
            <div className="h-3 bg-zinc-800 rounded w-4/5"></div>
            <div className="h-3 bg-zinc-800 rounded w-3/5"></div>
          </div>
        )}
        {joke && !loading && (
          <p
            className="text-white text-sm sm:text-base leading-relaxed transition-opacity duration-200"
            style={{ opacity: flipped ? 0 : 1 }}
          >
            {joke.response}
          </p>
        )}
      </div>

      <div className="flex gap-2 pt-1">
        {!joke ? (
          <Button
            onClick={fetchJoke}
            disabled={loading}
            className="flex-1 bg-gold-400 hover:bg-gold-500 text-black font-semibold rounded-xl h-10 sm:h-11 text-sm sm:text-base"
          >
            {loading ? <span className="animate-pulse">Loading…</span> : '🎲 Get Random Joke'}
          </Button>
        ) : (
          <>
            <Button
              onClick={handleNext}
              disabled={loading}
              className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-white font-semibold rounded-xl h-10 sm:h-11 text-sm border border-zinc-700"
            >
              {loading ? <span className="animate-pulse">…</span> : '🔀 Another One'}
            </Button>
            <button
              onClick={() => navigator.clipboard?.writeText(joke.response)}
              title="Copy joke"
              className="px-3 h-10 sm:h-11 rounded-xl bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-400 hover:text-white transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
          </>
        )}
      </div>
    </div>
  )
}


