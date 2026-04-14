import { useState, useCallback } from 'react'
import { useWebSocket } from './useWebSocket'
import { useJokeStore } from '@/store/jokeStore'

interface UseJokeWebSocketOptions {
  onComplete?: (fullText: string) => void
  onError?: (err: string) => void
}

export function useJokeWebSocket({ onComplete, onError }: UseJokeWebSocketOptions = {}) {
  const [streaming, setStreaming] = useState(false)
  const { setStreamingTokens, clearStream } = useJokeStore()

  const { send } = useWebSocket({
    onToken: (token: string) => {
      setStreamingTokens((prev) => prev + token)
    },
    onDone: (fullText: string) => {
      setStreaming(false)
      onComplete?.(fullText)
    },
    onError: (msg: string) => {
      setStreaming(false)
      onError?.(msg)
    }
  })

  const startStream = useCallback((query: string, style: string) => {
    clearStream()
    setStreaming(true)
    send(query, style)
  }, [send, clearStream])

  return { streaming, startStream }
}