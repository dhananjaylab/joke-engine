import { api } from './client'

export interface JokeResponse {
  id: number
  query: string
  response: string
  created_at: string
  share_count: number
  audio_url: string | null
  score_originality: number | null
  score_timing: number | null
  score_cleverness: number | null
}

export interface PaginatedJokes {
  jokes: JokeResponse[]
  total: number
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

  history: (page = 1) =>
    api.get<PaginatedJokes>(`/api/jokes/history?page=${page}`).then(r => r.data),

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
}
