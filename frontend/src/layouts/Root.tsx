import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import { NavBar } from '@/components/NavBar'
import { InstallBanner } from '@/components/InstallBanner'
import { useProfileStore } from '@/store/profileStore'
import { Toaster } from '@/components/ui/sonner'

export default function Root() {
  const fetchProfile = useProfileStore((s) => s.fetch)

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 transition-colors">
      <NavBar />
      <main className="max-w-lg mx-auto px-4 py-8">
        <Outlet />
      </main>
      <InstallBanner />
      <Toaster richColors />
    </div>
  )
}
