/**
 * FIX Phase-4: Replaced offset/page-number pagination with cursor-based
 * navigation.
 *
 * BEFORE: `page` state passed `?page=N` to the backend which used OFFSET —
 * O(n) scan that degrades as the joke table grows.
 *
 * AFTER:
 *  - `cursor` holds the last-seen joke ID for the current view.
 *  - `cursorStack` is a stack of previous cursors enabling "Previous" nav
 *    without re-querying all earlier pages.
 *  - `next_cursor === null` indicates the final page.
 *  - The query key includes the cursor so TanStack Query caches each page
 *    independently and navigating back is instant (served from cache).
 */
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { jokeApi } from '@/api/jokes'
import { JokeCard } from '@/components/JokeCard'
import { Button } from '@/components/ui/button'

const PAGE_SIZE = 8

export default function History() {
  // FIX Phase-4: cursor replaces page number
  const [cursor, setCursor] = useState<number | undefined>(undefined)
  const [cursorStack, setCursorStack] = useState<(number | undefined)[]>([])

  const qc = useQueryClient()
  const isFirstPage = cursorStack.length === 0

  const { data, isLoading } = useQuery({
    queryKey: ['jokes', 'history', cursor],
    queryFn: () => jokeApi.history(cursor, PAGE_SIZE),
    staleTime: 1000 * 30,   // 30s — history changes infrequently
  })

  const deleteMutation = useMutation({
    mutationFn: jokeApi.delete,
    onSuccess: () => {
      // Invalidate all history pages so counts stay consistent
      qc.invalidateQueries({ queryKey: ['jokes', 'history'] })
    },
  })

  const goNext = () => {
    if (!data?.next_cursor) return
    // Push current cursor onto the stack before advancing
    setCursorStack(prev => [...prev, cursor])
    setCursor(data.next_cursor)
  }

  const goPrev = () => {
    if (isFirstPage) return
    const stack = [...cursorStack]
    const prevCursor = stack.pop()
    setCursorStack(stack)
    setCursor(prevCursor)
  }

  // ── Derived display values ────────────────────────────────────────────────
  const pageNumber   = cursorStack.length + 1
  const hasNextPage  = Boolean(data?.next_cursor)
  const hasPrevPage  = !isFirstPage

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-pulse text-zinc-400">Loading your comedy history...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-white">Your Comedy History</h1>
        <p className="text-zinc-400">
          All the jokes you've generated
          {data?.total ? ` · ${data.total} total` : ''}
        </p>
      </div>

      {/* Joke list */}
      <div className="space-y-4">
        {data?.jokes.length === 0 && (
          <p className="text-zinc-500 text-center py-8">No jokes yet — generate your first one!</p>
        )}
        {data?.jokes.map((joke) => (
          <JokeCard
            key={joke.id}
            joke={joke}
            onDelete={(id) => deleteMutation.mutate(id)}
          />
        ))}
      </div>

      {/* Pagination controls */}
      {(hasPrevPage || hasNextPage) && (
        <div className="flex justify-between items-center pt-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={goPrev}
            disabled={!hasPrevPage}
            className="text-zinc-400 hover:text-white disabled:opacity-30"
          >
            ← Previous
          </Button>

          <span className="text-sm text-zinc-400">
            Page {pageNumber}
            {!hasNextPage ? ' (last)' : ''}
          </span>

          <Button
            variant="ghost"
            size="sm"
            onClick={goNext}
            disabled={!hasNextPage}
            className="text-zinc-400 hover:text-white disabled:opacity-30"
          >
            Next →
          </Button>
        </div>
      )}
    </div>
  )
}
