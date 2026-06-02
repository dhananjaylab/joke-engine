import { useState } from 'react'
import { Button } from './ui/button'

interface StructuredRoastProps {
  jokeId: number
  jokeText: string
  originality?: number | null
  timing?: number | null
  cleverness?: number | null
}

interface RoastData {
  overall_score: number
  roast: string
  breakdown: {
    originality: { score: number; comment: string }
    timing: { score: number; comment: string }
    cleverness: { score: number; comment: string }
  }
}

export function StructuredRoast({ jokeId, jokeText, originality, timing, cleverness }: StructuredRoastProps) {
  const [roastData, setRoastData] = useState<RoastData | null>(null)
  const [loading, setLoading] = useState(false)
  const [showRoast, setShowRoast] = useState(false)

  const generateRoast = async () => {
    if (roastData) {
      setShowRoast(!showRoast)
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`/api/jokes/${jokeId}/structured-roast`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          joke: jokeText,
          existing_scores: {
            originality: originality || null,
            timing: timing || null,
            cleverness: cleverness || null
          }
        }),
      })
      const data = await response.json()
      setRoastData(data)
      setShowRoast(true)
    } catch (error) {
      console.error('Structured roast error:', error)
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-400'
    if (score >= 6) return 'text-yellow-400'
    if (score >= 4) return 'text-orange-400'
    return 'text-red-400'
  }

  const getScoreEmoji = (score: number) => {
    if (score >= 8) return '🔥'
    if (score >= 6) return '👍'
    if (score >= 4) return '😐'
    return '💀'
  }

  return (
    <div className="space-y-3">
      <Button
        onClick={generateRoast}
        disabled={loading}
        variant="outline"
        className="bg-zinc-800/50 border-zinc-700 text-zinc-300 hover:bg-zinc-700 hover:text-white rounded-xl h-10 text-sm"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="animate-spin">⚡</span>
            Analyzing...
          </span>
        ) : showRoast ? (
          '🔥 Hide Roast'
        ) : (
          '🔥 Get Roasted'
        )}
      </Button>

      {showRoast && roastData && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 space-y-4 animate-in fade-in slide-in-from-top duration-300">
          {/* Overall Score */}
          <div className="text-center pb-3 border-b border-zinc-800">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="text-2xl">{getScoreEmoji(roastData.overall_score)}</span>
              <span className={`text-2xl font-bold ${getScoreColor(roastData.overall_score)}`}>
                {roastData.overall_score}/10
              </span>
            </div>
            <p className="text-xs text-zinc-500 uppercase tracking-wide">Overall Comedy Score</p>
          </div>

          {/* Detailed Breakdown */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-zinc-300 mb-2">📊 Detailed Analysis</h4>
            
            {Object.entries(roastData.breakdown).map(([category, data]) => (
              <div key={category} className="bg-zinc-800/30 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-zinc-400 capitalize">{category}</span>
                  <span className={`text-sm font-bold ${getScoreColor(data.score)}`}>
                    {data.score}/10
                  </span>
                </div>
                <p className="text-xs text-zinc-300 leading-relaxed">{data.comment}</p>
              </div>
            ))}
          </div>

          {/* The Roast */}
          <div className="border-t border-zinc-800 pt-4">
            <h4 className="text-sm font-medium text-zinc-300 mb-2 flex items-center gap-2">
              🎤 The Verdict
            </h4>
            <div className="bg-red-900/20 border border-red-800/50 rounded-lg p-3">
              <p className="text-sm text-zinc-300 leading-relaxed italic">
                "{roastData.roast}"
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}