import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { jokeApi } from '@/api/jokes'
import { JokeCard } from '@/components/JokeCard'
import { Button } from '@/components/ui/button'
import type { JokeResponse } from '@/api/jokes'

export default function Random() {
  const navigate = useNavigate()
  const [joke, setJoke] = useState<JokeResponse | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchRandomJoke = async () => {
    setLoading(true)
    try {
      const randomJoke = await jokeApi.randomJokes()
      setJoke(randomJoke)
    } catch (error) {
      console.error('Failed to fetch random joke:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRandomJoke()
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-pulse text-zinc-400">Loading random joke...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-white">Random Joke</h1>
        <p className="text-zinc-400">Fresh comedy from the API Ninjas vault</p>
      </div>

      {joke && (
        <div className="space-y-4">
          <JokeCard joke={joke} showActions={false} />
          
          <div className="flex gap-3 justify-center">
            <Button
              onClick={fetchRandomJoke}
              className="bg-gold-400 hover:bg-gold-500 text-black font-semibold"
            >
              🎲 Another Random Joke
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate('/')}
              className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
            >
              🏠 Back to Home
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}