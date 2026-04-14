import { useState, useEffect } from 'react'
import { Button } from './ui/button'

export function InstallBanner() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null)
  const [showBanner, setShowBanner] = useState(false)

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e)
      setShowBanner(true)
    }

    window.addEventListener('beforeinstallprompt', handler)
    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  const handleInstall = async () => {
    if (!deferredPrompt) return

    deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice
    
    if (outcome === 'accepted') {
      setShowBanner(false)
    }
    setDeferredPrompt(null)
  }

  if (!showBanner) return null

  return (
    <div className="fixed bottom-4 left-4 right-4 max-w-lg mx-auto bg-violet-600 text-white p-4 rounded-lg shadow-lg flex items-center justify-between gap-3">
      <div className="flex-1">
        <p className="font-medium">Install Giggle</p>
        <p className="text-sm text-violet-100">Get the app experience!</p>
      </div>
      <div className="flex gap-2">
        <Button variant="ghost" size="sm" onClick={() => setShowBanner(false)} className="text-white hover:bg-violet-700">
          Later
        </Button>
        <Button variant="outline" size="sm" onClick={handleInstall} className="bg-white text-violet-600 hover:bg-violet-50">
          Install
        </Button>
      </div>
    </div>
  )
}
