import { useState } from 'react'
import { Button } from './ui/button'
import { jokeApi } from '@/api/jokes'
import { toast } from 'sonner'

interface ShareButtonProps {
  readonly jokeId: number
  readonly jokeText: string
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
          url: globalThis.location.origin + `/joke/${jokeId}`,
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
    <Button 
      variant="outline" 
      size="sm" 
      onClick={handleShare} 
      disabled={loading}
      className="bg-zinc-800/50 border-zinc-700 text-zinc-300 hover:bg-zinc-700 hover:text-white"
    >
      {loading ? '...' : (
        <>
          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          Share
        </>
      )}
    </Button>
  )
}
