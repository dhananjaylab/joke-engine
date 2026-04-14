import { NavLink } from 'react-router-dom'
import { useThemeStore } from '@/store/themeStore'
import { useProfileStore } from '@/store/profileStore'

export function NavBar() {
  const { dark, toggle } = useThemeStore()
  const { xp, streak, rank } = useProfileStore()

  return (
    <nav className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
      <div className="max-w-lg mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <NavLink to="/" className="text-xl font-bold text-violet-600 dark:text-violet-400">
            Giggle
          </NavLink>
          <div className="flex gap-2 text-sm">
            <NavLink
              to="/"
              className={({ isActive }) =>
                isActive
                  ? 'text-violet-600 dark:text-violet-400 font-medium'
                  : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100'
              }
            >
              Home
            </NavLink>
            <NavLink
              to="/history"
              className={({ isActive }) =>
                isActive
                  ? 'text-violet-600 dark:text-violet-400 font-medium'
                  : 'text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100'
              }
            >
              History
            </NavLink>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-xs text-zinc-600 dark:text-zinc-400">
            <span className="font-medium">{rank}</span> · {xp} XP · 🔥 {streak}
          </div>
          <button
            onClick={toggle}
            className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
            aria-label="Toggle theme"
          >
            {dark ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
    </nav>
  )
}
