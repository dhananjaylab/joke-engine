import { useRef, useCallback, useEffect } from 'react'

interface UseWebSocketOptions {
  onToken: (text: string) => void
  onDone: (full: string) => void
  onError?: (msg: string) => void
}

export function useWebSocket({ onToken, onDone, onError }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/joke`)

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      if (msg.type === 'token') onToken(msg.text)
      else if (msg.type === 'done') onDone(msg.full)
      else if (msg.type === 'error') onError?.(msg.message)
    }

    ws.onclose = () => {}
    ws.onerror = () => onError?.('WebSocket connection failed')

    wsRef.current = ws
    return ws
  }, [onToken, onDone, onError])

  const send = useCallback((query: string, style: string) => {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      const newWs = connect()
      newWs.onopen = () => newWs.send(JSON.stringify({ query, style }))
    } else {
      ws.send(JSON.stringify({ query, style }))
    }
  }, [connect])

  useEffect(() => () => wsRef.current?.close(), [])

  return { send }
}
