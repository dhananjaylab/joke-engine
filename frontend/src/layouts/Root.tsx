import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import { NavBar } from '@/components/NavBar'
import { BottomNav } from '@/components/BottomNav'
import { InstallBanner } from '@/components/InstallBanner'
import { useProfileStore } from '@/store/profileStore'
import { Toaster } from '@/components/ui/sonner'

export default function Root() {
  const fetchProfile = useProfileStore((s) => s.fetch)

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  return (
    <div className="min-h-screen bg-zinc-950 transition-colors pb-20 sm:pb-0 flex flex-col">
      <NavBar />
      <main className="flex-1 max-w-4xl mx-auto px-4 py-6 sm:py-8 w-full">
        <Outlet />
      </main>
      <footer className="border-t border-zinc-800 py-4 sm:py-6 mt-8 sm:mt-12 hidden sm:block">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4 text-xs sm:text-sm text-zinc-500">
            <div>© 2024 GIGGLE GLOBAL. LAUGHTER IS UNIVERSAL.</div>
            <div className="flex gap-4 sm:gap-6">
              <a href="#" className="hover:text-zinc-300 transition-colors">ACCESSIBILITY</a>
              <a href="#" className="hover:text-zinc-300 transition-colors">REGION SWITCHER</a>
              <a href="#" className="hover:text-zinc-300 transition-colors">API</a>
              <a href="#" className="hover:text-zinc-300 transition-colors">CAREERS</a>
            </div>
          </div>
        </div>
      </footer>
      <BottomNav />
      <InstallBanner />
      <Toaster richColors />
    </div>
  )
}
