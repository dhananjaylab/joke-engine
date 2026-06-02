/**
 * FIX Phase-3: Memory leak eliminated.
 *
 * BEFORE: `useState(() => new Audio())` created an HTMLAudioElement that
 * was never cleaned up on unmount. Each row on the History page leaked one
 * live audio element that could be actively buffering network data.
 *
 * AFTER:
 *  - `useRef` holds the element (stable reference, no re-render on change).
 *  - A `useEffect` cleanup pauses playback and clears `audio.src`, which
 *    releases the network resource and unregisters all internal event listeners.
 */
import { useState, useRef, useEffect } from 'react'
import { Button } from './ui/button'

interface AudioPlayerProps {
  jokeId: number
}

export function AudioPlayer({ jokeId }: AudioPlayerProps) {
  const [playing, setPlaying] = useState(false)

  // FIX: useRef instead of useState — the element is stable across renders
  const audioRef = useRef<HTMLAudioElement>(new Audio())

  // FIX: cleanup on unmount — pauses and releases the network resource
  useEffect(() => {
    const audio = audioRef.current
    return () => {
      audio.pause()
      audio.src = ''   // signals the browser to release buffered data
    }
  }, [])

  const togglePlay = async () => {
    const audio = audioRef.current

    if (playing) {
      audio.pause()
      setPlaying(false)
    } else {
      audio.src = `/api/share/${jokeId}/audio`
      audio.onended = () => setPlaying(false)
      audio.onerror = () => setPlaying(false)
      try {
        await audio.play()
        setPlaying(true)
      } catch {
        // Autoplay blocked or network error — reset state silently
        setPlaying(false)
      }
    }
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={togglePlay}
      className="bg-zinc-800/50 border-zinc-700 text-zinc-300 hover:bg-zinc-700 hover:text-white"
    >
      {playing ? (
        <>
          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Pause
        </>
      ) : (
        <>
          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Listen
        </>
      )}
    </Button>
  )
}
