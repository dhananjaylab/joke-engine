import { useState } from 'react'
import { Button } from './ui/button'
import { jokeApi } from '@/api/jokes'
import { toast } from 'sonner'

interface ShareButtonProps {
  jokeId: number
  jokeText: string
}

export function ShareButton({ jokeId, jokeText }: ShareButtonProps) {
  const [loading, setLoading] = useState(false)

  const handleShare = async () => {
    setLoading(true)
    try {
      await jokeApi.incrementShare(jokeId)
      
      if (navigator.share) {
        await navigator.share({
          title: 'Giggle Joke',
          text: jokeText,
          url: window.location.origin + `/joke/${jokeId}`,
        })
      } else {
        await navigator.clipboard.writeText(jokeText)
        toast.success('Copied to clipboard!')
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        toast.error('Failed to share')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Button variant="outline" size="sm" onClick={handleShare} disabled={loading}>
      {loading ? '...' : '📤 Share'}
    </Button>
  )
}
