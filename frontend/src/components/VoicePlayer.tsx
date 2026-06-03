/**
 * FIX Phase-3: speechSynthesis resource leak eliminated.
 *
 * BEFORE: Navigating away while an utterance was speaking caused two bugs:
 *  1. Speech continued audibly after the component unmounted.
 *  2. The `onend` callback fired on the unmounted component, calling
 *     `setPlaying(false)` and triggering a React "state update on unmounted
 *     component" warning.
 *
 * AFTER: A `useEffect` cleanup unconditionally calls `speechSynthesis.cancel()`
 * on unmount, stopping speech and preventing the stale callback.
 */
import { useState, useRef, useEffect } from 'react'
import { Button } from './ui/button'

interface VoicePlayerProps {
  text: string
  jokeStyle?: string
}

const VOICE_TONES = [
  { id: 'default',    label: '🎭 Default',     voice: 'en-US-AriaNeural',    rate: 1.0, pitch: 1.0 },
  { id: 'comedian',   label: '😄 Comedian',    voice: 'en-US-GuyNeural',     rate: 1.1, pitch: 1.1 },
  { id: 'dramatic',   label: '🎪 Dramatic',    voice: 'en-US-JennyNeural',   rate: 0.9, pitch: 0.9 },
  { id: 'deadpan',    label: '😐 Deadpan',     voice: 'en-US-BrandonNeural', rate: 0.8, pitch: 0.8 },
  { id: 'excited',    label: '🤩 Excited',     voice: 'en-US-MichelleNeural', rate: 1.3, pitch: 1.2 },
  { id: 'sarcastic',  label: '😏 Sarcastic',   voice: 'en-US-RyanNeural',    rate: 0.9, pitch: 0.9 },
  { id: 'wise',       label: '🧙‍♂️ Wise',     voice: 'en-US-DavisNeural',   rate: 0.8, pitch: 0.7 },
  { id: 'valley-girl', label: '💅 Valley Girl', voice: 'en-US-AmberNeural',  rate: 1.1, pitch: 1.3 },
]

export function VoicePlayer({ text, jokeStyle }: VoicePlayerProps) {
  const [selectedTone, setSelectedTone] = useState('default')
  const [playing, setPlaying] = useState(false)
  const [showTones, setShowTones] = useState(false)
  // Track the active utterance so we can cancel it specifically
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null)

  // FIX: cancel any active utterance when the component unmounts
  useEffect(() => {
    return () => {
      if ('speechSynthesis' in window) {
        speechSynthesis.cancel()
      }
      utteranceRef.current = null
    }
  }, [])

  const playWithTone = async (toneId: string) => {
    if (playing) {
      if ('speechSynthesis' in window) speechSynthesis.cancel()
      setPlaying(false)
      return
    }

    const tone = VOICE_TONES.find(t => t.id === toneId) ?? VOICE_TONES[0]

    if (!('speechSynthesis' in window)) return

    // Cancel anything already speaking
    speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utteranceRef.current = utterance

    const voices = speechSynthesis.getVoices()
    const voice =
      voices.find(v => v.name.includes(tone.voice.split('-')[2])) ??
      voices.find(v => v.lang === 'en-US') ??
      voices[0]

    if (voice) utterance.voice = voice
    utterance.rate  = tone.rate
    utterance.pitch = tone.pitch

    utterance.onstart = () => setPlaying(true)
    utterance.onend   = () => {
      // Guard: only update state if this utterance is still current
      if (utteranceRef.current === utterance) {
        setPlaying(false)
        utteranceRef.current = null
      }
    }
    utterance.onerror = () => {
      if (utteranceRef.current === utterance) {
        setPlaying(false)
        utteranceRef.current = null
      }
    }

    speechSynthesis.speak(utterance)
    setSelectedTone(toneId)
  }

  const stopSpeech = () => {
    if ('speechSynthesis' in window) speechSynthesis.cancel()
    setPlaying(false)
    utteranceRef.current = null
  }

  const getRecommendedTone = (): string => {
    if (!jokeStyle) return 'default'
    const map: Record<string, string> = {
      sarcastic: 'sarcastic', deadpan: 'deadpan', dad: 'wise',
      roast: 'comedian', dark: 'dramatic', 'gen-z': 'valley-girl',
      millennial: 'excited', boomer: 'wise',
    }
    return map[jokeStyle] ?? 'default'
  }

  return (
    <div className="space-y-3">
      {/* Main play/stop controls */}
      <div className="flex items-center gap-2">
        <Button
          onClick={() => playWithTone(selectedTone)}
          disabled={!text.trim()}
          className="bg-gold-400 hover:bg-gold-500 text-black font-semibold rounded-xl h-10 text-sm flex items-center gap-2"
        >
          {playing ? (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6" />
              </svg>
              Stop
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 14.142M8.464 8.464L12 12l-3.536 3.536M21 12H3" />
              </svg>
              🎤 Listen
            </>
          )}
        </Button>

        <Button
          onClick={() => setShowTones(!showTones)}
          variant="outline"
          className="bg-zinc-800/50 border-zinc-700 text-zinc-300 hover:bg-zinc-700 hover:text-white rounded-xl h-10 text-sm"
        >
          {showTones ? 'Hide Tones' : 'Voice Tones'}
          <svg className={`w-4 h-4 ml-1 transition-transform ${showTones ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </Button>

        {playing && (
          <Button
            onClick={stopSpeech}
            variant="outline"
            className="bg-red-900/50 border-red-700 text-red-300 hover:bg-red-800 rounded-xl h-10 text-sm"
          >
            ⏹️ Stop
          </Button>
        )}
      </div>

      {/* Tone selector panel */}
      {showTones && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 space-y-3 animate-in fade-in slide-in-from-top duration-300">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm font-medium text-zinc-300">Choose Voice Tone:</span>
            {jokeStyle && (
              <Button
                onClick={() => {
                  const recommended = getRecommendedTone()
                  setSelectedTone(recommended)
                  playWithTone(recommended)
                }}
                className="text-xs bg-gold-400/20 text-gold-400 border border-gold-400/30 hover:bg-gold-400/30 rounded-lg px-2 py-1 h-auto"
              >
                ✨ Auto-match style
              </Button>
            )}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {VOICE_TONES.map((tone) => (
              <button
                key={tone.id}
                onClick={() => playWithTone(tone.id)}
                className={`p-2 rounded-lg text-xs font-medium transition-all border ${
                  selectedTone === tone.id
                    ? 'bg-gold-400/20 border-gold-400/50 text-gold-400'
                    : 'bg-zinc-800/50 border-zinc-700 text-zinc-300 hover:bg-zinc-700'
                }`}
              >
                {tone.label}
              </button>
            ))}
          </div>

          <p className="text-xs text-zinc-500 text-center">
            💡 Different tones work better with different joke styles!
          </p>
        </div>
      )}
    </div>
  )
}
