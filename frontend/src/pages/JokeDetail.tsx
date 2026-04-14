import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { jokeApi } from '@/api/jokes'
import { JokeCard } from '@/components/JokeCard'

export default function JokeDetail() {
  const { id } = useParams<{ id: string }>()
  
  const { data: joke, isLoading } = useQuery({
    queryKey: ['joke', id],
    queryFn: () => jokeApi.getById(Number(id)),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-12 text-zinc-400 text-sm">Loading…</div>
    )
  }

  if (!joke) {
    return (
      <div className="text-center py-12">
        <p className="text-zinc-600 dark:text-zinc-400">Joke not found</p>
      </div>
    )
  }

  return (
    <div>
      <JokeCard joke={joke} showActions={true} />
    </div>
  )
}
