/**
 * FIX Phase-4: history() now uses cursor-based pagination.
 *
 * BEFORE: history(page: number) passed `?page=N` — the backend used OFFSET
 * which degrades as the dataset grows.
 *
 * AFTER: history(cursor?) passes `?cursor=<lastId>` — the backend uses a
 * keyset WHERE clause that is O(log n) regardless of dataset size.
 * `next_cursor` from the response is passed as the cursor for the next page.
 */
import { api } from './client'

export interface JokeResponse {
  id: number
  query: string
  response: string
  source: string
  session_key: string | null
  created_at: string
  share_count: number
  audio_url: string | null
  score_originality: number | null
  score_timing: number | null
  score_cleverness: number | null
  // Optional style field used by JokeCard badge
  style?: string
}

/** FIX Phase-4: cursor-based response — next_cursor replaces page/pages */
export interface PaginatedJokes {
  jokes: JokeResponse[]
  total: number
  next_cursor: number | null   // pass as ?cursor= on next request; null = last page
  // Legacy fields kept for backwards compat during migration
  page: number
  pages: number
}

export interface GenerateRequest {
  query: string
  style: string
  regenerate?: boolean
}

export const jokeApi = {
  generate: (body: GenerateRequest) =>
    api.post<JokeResponse>('/api/jokes/generate', body).then(r => r.data),

  /**
   * FIX Phase-4: cursor-based history.
   * Pass cursor = undefined for the first page.
   * Pass cursor = response.next_cursor for subsequent pages.
   */
  history: (cursor?: number, pageSize = 8) => {
    const params = new URLSearchParams({ page_size: String(pageSize) })
    if (cursor !== undefined) params.set('cursor', String(cursor))
    return api
      .get<PaginatedJokes>(`/api/jokes/history?${params}`)
      .then(r => r.data)
  },

  getById: (id: number) =>
    api.get<JokeResponse>(`/api/jokes/${id}`).then(r => r.data),

  delete: (id: number) =>
    api.delete(`/api/jokes/${id}`),

  heckle: (joke: string) =>
    api.post<{ roast: string }>('/api/heckle', { joke }).then(r => r.data),

  explain: (id: number) =>
    api.post<{ explanation: string }>(`/api/jokes/${id}/explain`).then(r => r.data),

  incrementShare: (id: number) =>
    api.post(`/api/share/${id}/increment`),

  jokeOfTheDay: () =>
    api.get<{ joke: string }>('/api/jokes/joke-of-the-day').then(r => r.data),

  randomJokes: () =>
    api.get<JokeResponse>('/api/jokes/random').then(r => r.data),
}
