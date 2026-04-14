import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api } from '@/api/client'

interface ProfileStore {
  xp: number
  streak: number
  rank: string
  lastFetched: number | null
  fetch: () => Promise<void>
}

export const useProfileStore = create<ProfileStore>()(
  persist(
    (set) => ({
      xp: 0,
      streak: 0,
      rank: 'Open Mic',
      lastFetched: null,
      fetch: async () => {
        try {
          const { data } = await api.get('/api/profile')
          set({ xp: data.xp, streak: data.streak, rank: data.rank, lastFetched: Date.now() })
        } catch (e) {
          console.warn('Profile fetch failed:', e)
        }
      },
    }),
    { name: 'giggle-profile' }
  )
)
