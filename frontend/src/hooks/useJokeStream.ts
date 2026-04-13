import { useState, useCallback, useRef } from 'react'

interface UseJokeStreamOptions {
  onComplete?: (fullText: string) => void
  onError?: (err: Error) => void
}

export function useJokeStream({ onComplete, onError }: UseJokeStreamOptions = {}) {
  const [tokens, setTokens] = useState('')
  const [streaming, setStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const startStream = useCallback(async (query: string, style: string) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setTokens('')
    setStreaming(true)

    const url = `/api/jokes/stream?query=${encodeURIComponent(query)}&style=${encodeURIComponent(style)}`

    try {
      const res = await fetch(url, {
        signal: controller.signal,
        credentials: 'include',
      })

      if (!res.ok) throw new Error(`Stream failed: ${res.status}`)
      if (!res.body) throw new Error('No response body')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      const accumulated: string[] = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value, { stream: true })
        for (const line of text.split('\n')) {
          if (line.startsWith('data: ')) {
            const token = line.slice(6)
            if (token === '[DONE]') {
              const full = accumulated.join('')
              onComplete?.(full)
              break
            }
            accumulated.push(token)
            setTokens(prev => prev + token)
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        onError?.(err as Error)
      }
    } finally {
      setStreaming(false)
    }
  }, [onComplete, onError])

  const cancel = useCallback(() => abortRef.current?.abort(), [])

  return { tokens, streaming, startStream, cancel }
}
