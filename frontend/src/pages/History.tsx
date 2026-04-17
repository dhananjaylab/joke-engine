import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { jokeApi } from '@/api/jokes'
import { JokeCard } from '@/components/JokeCard'
import { Button } from '@/components/ui/button'

export default function History() {
  const [page, setPage] = useState(1)
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['jokes', 'history', page],
    queryFn: () => jokeApi.history(page),
  })

  const deleteMutation = useMutation({
    mutationFn: jokeApi.delete,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['jokes', 'history'] }),
  })

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
        <p className="text-zinc-400">All the jokes you've generated</p>
      </div>

      <div className="space-y-4">
        {data?.jokes.map((joke) => (
          <JokeCard key={joke.id} joke={joke} onDelete={(id) => deleteMutation.mutate(id)} />
        ))}
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center pt-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setPage((p) => p - 1)}
          disabled={page <= 1}
          className="text-zinc-400 hover:text-white"
        >
          ← Previous
        </Button>
        <span className="text-sm text-zinc-400">
          Page {page} of {data?.pages ?? 1}
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setPage((p) => p + 1)}
          disabled={page >= (data?.pages ?? 1)}
          className="text-zinc-400 hover:text-white"
        >
          Next →
        </Button>
      </div>
    </div>
  )
}
