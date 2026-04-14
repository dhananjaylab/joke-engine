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
    <Button variant="outline" size="sm" onClick={togglePlay}>
      {playing ? '⏸️ Pause' : '🔊 Listen'}
    </Button>
  )
}
