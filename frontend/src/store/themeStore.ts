import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ThemeStore {
  dark: boolean
  toggle: () => void
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      dark: window.matchMedia('(prefers-color-scheme: dark)').matches,
      toggle: () => {
        const next = !get().dark
        document.documentElement.classList.toggle('dark', next)
        set({ dark: next })
      },
    }),
    { name: 'giggle-theme' }
  )
)

// Apply on load
const stored = JSON.parse(localStorage.getItem('giggle-theme') ?? '{}')
if (stored?.state?.dark) document.documentElement.classList.add('dark')
