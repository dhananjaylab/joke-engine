import { NavLink } from 'react-router-dom'
import { useProfileStore } from '@/store/profileStore'

export function NavBar() {
  const { xp, streak } = useProfileStore()

  return (
    <nav className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-3 sm:py-4 flex items-center justify-between">
        {/* Logo and Navigation */}
        <div className="flex items-center gap-4 sm:gap-6">
          <NavLink to="/" className="text-xl sm:text-2xl font-bold tracking-tight">
            <span className="text-gold-400">GIGGLE</span>
          </NavLink>
          <div className="hidden md:flex gap-6 text-sm">
            <NavLink
              to="/"
              className={({ isActive }) =>
                isActive
                  ? 'text-white font-medium'
                  : 'text-zinc-400 hover:text-white transition-colors'
              }
            >
              Discover
            </NavLink>
            <NavLink
              to="/history"
              className={({ isActive }) =>
                isActive
                  ? 'text-white font-medium'
                  : 'text-zinc-400 hover:text-white transition-colors'
              }
            >
              Live
            </NavLink>
            <NavLink
              to="/battle"
              className={({ isActive }) =>
                isActive
                  ? 'text-white font-medium'
                  : 'text-zinc-400 hover:text-white transition-colors'
              }
            >
              Rising
            </NavLink>
          </div>
        </div>

        {/* Stats and Profile */}
        <div className="flex items-center gap-2 sm:gap-4">
          <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm">
            <div className="flex items-center gap-1 sm:gap-1.5 text-gold-400">
              <span className="text-sm sm:text-base">⭐</span>
              <span className="font-semibold">{xp} XP</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 text-orange-400">
              <span>🔥</span>
              <span className="font-semibold">{streak} Hot Streak</span>
            </div>
            <button className="hidden sm:flex items-center gap-1.5 text-zinc-400 hover:text-white transition-colors">
              <span>🌐</span>
              <span className="hidden lg:inline">Language</span>
            </button>
          </div>
          <button className="p-1.5 sm:p-2 rounded-full hover:bg-zinc-800 transition-colors">
            <svg className="w-5 h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </button>
        </div>
      </div>
    </nav>
  )
}
