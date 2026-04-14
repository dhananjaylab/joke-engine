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
      <div className="flex justify-center py-12 text-zinc-400 text-sm">Loading…</div>
    )
  }

  return (
    <div className="space-y-4">
      {data?.jokes.map((joke) => (
        <JokeCard key={joke.id} joke={joke} onDelete={(id) => deleteMutation.mutate(id)} />
      ))}

      {/* Pagination */}
      <div className="flex justify-between items-center pt-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setPage((p) => p - 1)}
          disabled={page <= 1}
        >
          Previous
        </Button>
        <span className="text-xs text-zinc-400">
          {page} / {data?.pages ?? 1}
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setPage((p) => p + 1)}
          disabled={page >= (data?.pages ?? 1)}
        >
          Next
        </Button>
      </div>
    </div>
  )
}
