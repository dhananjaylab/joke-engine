/**
 * Global test setup — runs before every test file.
 * Polyfills and global mocks that all tests rely on live here.
 */
import '@testing-library/jest-dom'
import { vi } from 'vitest'

// ── requestAnimationFrame / cancelAnimationFrame ──────────────────────────────
// jsdom does not implement rAF. We provide a queue-based implementation so
// tests can flush pending callbacks on demand via `flushRaf()`.

export const _rafQueue: Map<number, FrameRequestCallback> = new Map()
let _rafId = 0

export function installRafMock(): void {
  vi.stubGlobal('requestAnimationFrame', (cb: FrameRequestCallback): number => {
    const id = ++_rafId
    _rafQueue.set(id, cb)
    return id
  })

  vi.stubGlobal('cancelAnimationFrame', (id: number): void => {
    _rafQueue.delete(id)
  })
}

installRafMock()

/** Flush all pending rAF callbacks in queue order. */
export function flushRaf(): void {
  const entries = [..._rafQueue.entries()]
  _rafQueue.clear()
  entries.forEach(([, cb]) => cb(performance.now()))
}

// Reset the rAF queue between tests
afterEach(() => {
  _rafQueue.clear()
})
