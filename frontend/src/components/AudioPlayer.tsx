import { useState } from 'react'
import { Button } from './ui/button'

interface AudioPlayerProps {
  jokeId: number
}

export function AudioPlayer({ jokeId }: AudioPlayerProps) {
  const [playing, setPlaying] = useState(false)
  const [audio] = useState(() => new Audio())

  const togglePlay = async () => {
    if (playing) {
      audio.pause()
      setPlaying(false)
    } else {
      audio.src = `/api/share/${jokeId}/audio`
      audio.onended = () => setPlaying(false)
      await audio.play()
      setPlaying(true)
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
