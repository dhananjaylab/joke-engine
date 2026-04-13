import { create } from 'zustand'

interface JokeStore {
  currentJoke: string | null
  currentJokeId: number | null
  currentStyle: string
  streamingTokens: string
  setJoke: (joke: string, id: number) => void
  setStyle: (style: string) => void
  setStreamingTokens: (t: string) => void
  appendToken: (token: string) => void
  clearStream: () => void
}

export const useJokeStore = create<JokeStore>()((set) => ({
  currentJoke: null,
  currentJokeId: null,
  currentStyle: 'witty',
  streamingTokens: '',
  setJoke: (joke, id) => set({ currentJoke: joke, currentJokeId: id, streamingTokens: '' }),
  setStyle: (style) => set({ currentStyle: style }),
  setStreamingTokens: (t) => set({ streamingTokens: t }),
  appendToken: (token) => set((s) => ({ streamingTokens: s.streamingTokens + token })),
  clearStream: () => set({ streamingTokens: '' }),
}))
