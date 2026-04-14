import { Button } from './ui/button'

interface StreamingToggleProps {
  useWebSocket: boolean
  onChange: (useWebSocket: boolean) => void
}

export function StreamingToggle({ useWebSocket, onChange }: StreamingToggleProps) {
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-zinc-500">Stream:</span>
      <Button
        variant={useWebSocket ? "outline" : "default"}
        size="sm"
        onClick={() => onChange(false)}
        className="h-6 px-2 text-xs"
      >
        SSE
      </Button>
      <Button
        variant={useWebSocket ? "default" : "outline"}
        size="sm"
        onClick={() => onChange(true)}
        className="h-6 px-2 text-xs"
      >
        WS
      </Button>
    </div>
  )
}