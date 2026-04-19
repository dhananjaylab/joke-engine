import { NavLink } from 'react-router-dom'

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-zinc-900/95 backdrop-blur-lg border-t border-zinc-800 sm:hidden z-50">
      <div className="flex items-center justify-around px-2 py-3">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex flex-col items-center gap-1 transition-all duration-200 px-3 py-1 rounded-lg ${
              isActive 
                ? 'text-gold-400 bg-gold-400/10' 
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
            }`
          }
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span className="text-xs font-medium">Home</span>
        </NavLink>

        <NavLink
          to="/random"
          className={({ isActive }) =>
            `flex flex-col items-center gap-1 transition-all duration-200 px-3 py-1 rounded-lg ${
              isActive 
                ? 'text-gold-400 bg-gold-400/10' 
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
            }`
          }
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span className="text-xs font-medium">Random</span>
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `flex flex-col items-center gap-1 transition-all duration-200 px-3 py-1 rounded-lg ${
              isActive 
                ? 'text-gold-400 bg-gold-400/10' 
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
            }`
          }
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-xs font-medium">History</span>
        </NavLink>

        <NavLink
          to="/profile"
          className={({ isActive }) =>
            `flex flex-col items-center gap-1 transition-all duration-200 px-3 py-1 rounded-lg ${
              isActive 
                ? 'text-gold-400 bg-gold-400/10' 
                : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
            }`
          }
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span className="text-xs font-medium">Profile</span>
        </NavLink>
      </div>
    </nav>
  )
}