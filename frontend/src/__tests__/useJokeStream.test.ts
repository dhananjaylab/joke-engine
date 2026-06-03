/**
 * Tests for useJokeStream — validates every fix applied in Phase-2 and Phase-3.
 *
 * Coverage:
 *  ✓ Phase-2 rAF batching: burst of N tokens causes ≤ N/5 state updates
 *  ✓ Phase-2 final flush:  [DONE] forces an immediate flush bypassing rAF
 *  ✓ JOKE_ID parsing:      [JOKE_ID:42] extracted and forwarded to onComplete
 *  ✓ Abort:                cancel() stops the stream mid-flight
 *  ✓ Error path:           onError called on fetch failure
 *  ✓ Abort not an error:   AbortError is silently ignored
 *  ✓ Buffer cleared:       restarting a stream resets previous accumulation
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useJokeStream } from '../hooks/useJokeStream'
import { flushRaf, _rafQueue } from './setup'

// ── Store mock ────────────────────────────────────────────────────────────────
const mockSetStreamingTokens = vi.fn()
const mockClearStream        = vi.fn()

vi.mock('@/store/jokeStore', () => ({
  useJokeStore: () => ({
    setStreamingTokens: mockSetStreamingTokens,
    clearStream:        mockClearStream,
  }),
}))

// ── Fetch helpers ─────────────────────────────────────────────────────────────

const encoder = new TextEncoder()

/** Build a mock Response whose body streams the given SSE lines. */
function mockSseResponse(lines: string[]): Response {
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const line of lines) {
        controller.enqueue(encoder.encode(line))
      }
      controller.close()
    },
  })
  return new Response(stream, { status: 200 })
}

/** SSE framing for a plain token. */
const tokenLine = (t: string) => `data: ${t}\n\n`

/** Build a complete SSE conversation: N tokens + optional JOKE_ID + DONE. */
function buildSseLines(tokens: string[], jokeId?: number): string[] {
  const lines = tokens.map(tokenLine)
  if (jokeId !== undefined) lines.push(`data: [JOKE_ID:${jokeId}]\n\n`)
  lines.push('data: [DONE]\n\n')
  return lines
}

// ── Setup / teardown ──────────────────────────────────────────────────────────

beforeEach(() => {
  vi.restoreAllMocks()
  mockSetStreamingTokens.mockClear()
  mockClearStream.mockClear()
})

afterEach(() => {
  vi.unstubAllGlobals()
})

// ─────────────────────────────────────────────────────────────────────────────
// Phase-2 regression: rAF token batching
// ─────────────────────────────────────────────────────────────────────────────

describe('rAF token batching (Phase-2)', () => {
  it('accumulates 20 tokens but updates state only once on [DONE]', async () => {
    const tokens = Array.from({ length: 20 }, (_, i) => `w${i} `)
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      mockSseResponse(buildSseLines(tokens))
    ))

    const { result } = renderHook(() => useJokeStream({}))

    await act(async () => {
      await result.current.startStream('cats', 'witty')
    })

    // [DONE] forces an immediate flush — exactly ONE state update with full text
    expect(mockSetStreamingTokens).toHaveBeenCalledTimes(1)
    expect(mockSetStreamingTokens).toHaveBeenCalledWith(tokens.join(''))
  })

  it('rAF queue is empty after stream completes (no leaked callbacks)', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      mockSseResponse(buildSseLines(['hello ', 'world']))
    ))

    const { result } = renderHook(() => useJokeStream({}))

    await act(async () => {
      await result.current.startStream('cats', 'witty')
    })

    expect(_rafQueue.size).toBe(0)
  })

  it('mid-stream rAF fires with partial text before [DONE]', async () => {
    // Simulate 5 tokens arriving, then flush rAF, then [DONE]
    const partialTokens = ['one ', 'two ', 'three ', 'four ', 'five ']

    // We need to interleave: tokens → flush rAF → DONE
    // Achieve this with a slow stream that yields control
    let resolveSecondChunk!: () => void
    const pausePromise = new Promise<void>(r => { resolveSecondChunk = r })

    const stream = new ReadableStream<Uint8Array>({
      async start(controller) {
        // First chunk: 5 tokens
        for (const t of partialTokens) controller.enqueue(encoder.encode(tokenLine(t)))
        // Pause so rAF can fire
        await pausePromise
        // Second chunk: DONE
        controller.enqueue(encoder.encode('data: [DONE]\n\n'))
        controller.close()
      },
    })

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(stream, { status: 200 })))

    const { result } = renderHook(() => useJokeStream({}))

    // Start stream but keep the promise so the pending work can be awaited later.
    let streamPromise!: Promise<void>
    act(() => {
      streamPromise = result.current.startStream('cats', 'witty')
    })

    // Give the first chunk time to be processed
    await new Promise(r => setTimeout(r, 10))

    await waitFor(() => expect(_rafQueue.size).toBeGreaterThan(0))
    // Flush rAF — should update state with partial text
    flushRaf()
    expect(mockSetStreamingTokens).toHaveBeenCalledWith(partialTokens.join(''))

    // Resume the stream to completion
    resolveSecondChunk()
    await act(async () => {
      await streamPromise
    })

    // Final [DONE] update
    const lastCall = mockSetStreamingTokens.mock.calls.at(-1)![0]
    expect(lastCall).toBe(partialTokens.join(''))
  })
})

// ─────────────────────────────────────────────────────────────────────────────
// JOKE_ID parsing
// ─────────────────────────────────────────────────────────────────────────────

describe('JOKE_ID extraction', () => {
  it('parses [JOKE_ID:42] and forwards the id to onComplete', async () => {
    const onComplete = vi.fn()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      mockSseResponse(buildSseLines(['A funny joke.'], 42))
    ))

    const { result } = renderHook(() => useJokeStream({ onComplete }))

    await act(async () => {
      await result.current.startStream('cats', 'witty')
    })

    expect(onComplete).toHaveBeenCalledOnce()
    expect(onComplete).toHaveBeenCalledWith('A funny joke.', 42)
  })

  it('calls onComplete with undefined jokeId when no JOKE_ID line present', async () => {
    const onComplete = vi.fn()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      mockSseResponse(buildSseLines(['No id here.']))
    ))

    const { result } = renderHook(() => useJokeStream({ onComplete }))

    await act(async () => {
      await result.current.startStream('cats', 'witty')
    })

    expect(onComplete).toHaveBeenCalledWith('No id here.', undefined)
  })
})

// ─────────────────────────────────────────────────────────────────────────────
// Streaming state flag
// ─────────────────────────────────────────────────────────────────────────────

describe('streaming state', () => {
  it('is true during streaming and false after completion', async () => {
    let resolveStream!: () => void
    const stream = new ReadableStream<Uint8Array>({
      async start(controller) {
        controller.enqueue(encoder.encode(tokenLine('hello')))
        await new Promise<void>(r => { resolveStream = r })
        controller.enqueue(encoder.encode('data: [DONE]\n\n'))
        controller.close()
      },
    })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(stream, { status: 200 })))

    const { result } = renderHook(() => useJokeStream({}))
    expect(result.current.streaming).toBe(false)

    // Start, don't await
    act(() => { result.current.startStream('test', 'witty') })
    await new Promise(r => setTimeout(r, 10))
    expect(result.current.streaming).toBe(true)

    // Complete the stream
    await act(async () => { resolveStream() })
    await new Promise(r => setTimeout(r, 10))
    expect(result.current.streaming).toBe(false)
  })
})

// ─────────────────────────────────────────────────────────────────────────────
// Abort / cancel
// ─────────────────────────────────────────────────────────────────────────────

describe('cancel()', () => {
  it('aborts an in-flight stream without calling onError', async () => {
    const onError    = vi.fn()
    const onComplete = vi.fn()

    let resolveStream!: () => void
    const stream = new ReadableStream<Uint8Array>({
      async start(controller) {
        controller.enqueue(encoder.encode(tokenLine('partial')))
        await new Promise<void>(r => { resolveStream = r })
        controller.enqueue(encoder.encode('data: [DONE]\n\n'))
        controller.close()
      },
    })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(stream, { status: 200 })))

    const { result } = renderHook(() => useJokeStream({ onComplete, onError }))

    // Start stream
    act(() => { result.current.startStream('test', 'witty') })
    await new Promise(r => setTimeout(r, 10))

    // Cancel mid-flight
    act(() => { result.current.cancel() })

    // Clean up the dangling stream
    resolveStream()
    await new Promise(r => setTimeout(r, 10))

    expect(onError).not.toHaveBeenCalled()
    expect(onComplete).not.toHaveBeenCalled()
  })

  it('starting a new stream cancels the previous one', async () => {
    let resolveFirst!: () => void
    const firstStream = new ReadableStream<Uint8Array>({
      async start(controller) {
        controller.enqueue(encoder.encode(tokenLine('first')))
        await new Promise<void>(r => { resolveFirst = r })
        controller.close()
      },
    })

    const secondLines = buildSseLines(['second'])
    const secondStream = mockSseResponse(secondLines)

    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(firstStream, { status: 200 }))
      .mockResolvedValueOnce(secondStream)

    vi.stubGlobal('fetch', fetchMock)

    const onComplete = vi.fn()
    const { result } = renderHook(() => useJokeStream({ onComplete }))

    // Start first stream
    act(() => { result.current.startStream('first', 'witty') })
    await new Promise(r => setTimeout(r, 10))

    // Start second stream — should cancel first
    await act(async () => {
      await result.current.startStream('second', 'witty')
    })

    resolveFirst() // clean up

    // Only the second stream's onComplete should fire
    expect(onComplete).toHaveBeenCalledTimes(1)
    expect(onComplete).toHaveBeenCalledWith('second', undefined)
  })
})

// ─────────────────────────────────────────────────────────────────────────────
// Error handling
// ─────────────────────────────────────────────────────────────────────────────

describe('error handling', () => {
  it('calls onError when fetch rejects', async () => {
    const onError = vi.fn()
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network failure')))

    const { result } = renderHook(() => useJokeStream({ onError }))

    await act(async () => {
      await result.current.startStream('cats', 'witty')
    })

    expect(onError).toHaveBeenCalledOnce()
    expect(onError.mock.calls[0][0]).toBeInstanceOf(Error)
    expect((onError.mock.calls[0][0] as Error).message).toBe('Network failure')
  })

  it('calls onError when the server returns a non-200 status', async () => {
    const onError = vi.fn()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(null, { status: 503 })
    ))

    const { result } = renderHook(() => useJokeStream({ onError }))

    await act(async () => {
      await result.current.startStream('cats', 'witty')
    })

    expect(onError).toHaveBeenCalledOnce()
  })

  it('does NOT call onError for an AbortError', async () => {
    const onError = vi.fn()
    const abortError = new DOMException('The operation was aborted', 'AbortError')
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(abortError))

    const { result } = renderHook(() => useJokeStream({ onError }))

    await act(async () => {
      await result.current.startStream('cats', 'witty')
    })

    expect(onError).not.toHaveBeenCalled()
  })

  it('sets streaming=false even when an error occurs', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('fail')))

    const { result } = renderHook(() => useJokeStream({}))

    await act(async () => {
      await result.current.startStream('cats', 'witty')
    })

    expect(result.current.streaming).toBe(false)
  })
})

// ─────────────────────────────────────────────────────────────────────────────
// Buffer reset between streams
// ─────────────────────────────────────────────────────────────────────────────

describe('buffer reset', () => {
  it('does not bleed tokens from a previous stream into the next', async () => {
    const onComplete = vi.fn()

    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(mockSseResponse(buildSseLines(['first joke.'])))
      .mockResolvedValueOnce(mockSseResponse(buildSseLines(['second joke.'])))
    )

    const { result } = renderHook(() => useJokeStream({ onComplete }))

    await act(async () => { await result.current.startStream('q1', 'witty') })
    await act(async () => { await result.current.startStream('q2', 'witty') })

    const calls = onComplete.mock.calls
    expect(calls).toHaveLength(2)
    expect(calls[0][0]).toBe('first joke.')
    expect(calls[1][0]).toBe('second joke.')   // must NOT include 'first joke.'
  })

  it('calls clearStream on each new startStream invocation', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      mockSseResponse(buildSseLines(['hello']))
    ))

    const { result } = renderHook(() => useJokeStream({}))

    await act(async () => { await result.current.startStream('q1', 'witty') })
    await act(async () => { await result.current.startStream('q2', 'witty') })

    expect(mockClearStream).toHaveBeenCalledTimes(2)
  })
})
