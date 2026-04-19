import { useState, useRef, useEffect } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useJokeStore } from '@/store/jokeStore'
import { StyleSelect } from './StyleSelect'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { ShareButton } from './ShareButton'
import { toast } from 'sonner'

export function NavBar() {
  const navigate = useNavigate()
  const { currentJoke, currentJokeId, currentStyle, setStyle } = useJokeStore()
  
  // Search state
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const searchRef = useRef<HTMLInputElement>(null)
  
  // Settings dropdown
  const [settingsOpen, setSettingsOpen] = useState(false)
  const settingsRef = useRef<HTMLDivElement>(null)
  
  // Recently used topics (stored in localStorage)
  const [recentTopics, setRecentTopics] = useState<string[]>(() => {
    try {
      return JSON.parse(localStorage.getItem('recentTopics') || '[]')
    } catch {
      return []
    }
  })

  // Close dropdowns on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (settingsRef.current && !settingsRef.current.contains(e.target as Node)) {
        setSettingsOpen(false)
      }
    }
    if (settingsOpen) document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [settingsOpen])

  // Focus search when opened
  useEffect(() => {
    if (searchOpen && searchRef.current) {
      searchRef.current.focus()
    }
  }, [searchOpen])

  const handleQuickGenerate = () => {
    if (!searchQuery.trim()) return
    
    // Add to recent topics
    const newRecents = [searchQuery, ...recentTopics.filter(t => t !== searchQuery)].slice(0, 5)
    setRecentTopics(newRecents)
    localStorage.setItem('recentTopics', JSON.stringify(newRecents))
    
    // Navigate to home with query
    navigate('/', { state: { query: searchQuery, style: currentStyle } })
    setSearchQuery('')
    setSearchOpen(false)
  }

  const handleRandomJoke = async () => {
    navigate('/random')
  }

  return (
    <nav className="border-b border-zinc-800 bg-zinc-900/80 backdrop-blur-md sticky top-0 z-50 transition-all duration-200">
      <div className="max-w-6xl mx-auto px-4 py-3 sm:py-4">
        <div className="flex items-center justify-between gap-4">
          {/* Logo and Main Navigation */}
          <div className="flex items-center gap-6">
            <NavLink 
              to="/" 
              className="text-xl sm:text-2xl font-bold tracking-tight hover:scale-105 transition-transform duration-200"
            >
              <span className="text-gold-400">GIGGLE</span>
            </NavLink>
            
            <div className="hidden lg:flex gap-8 text-sm font-medium">
              <NavLink
                to="/"
                className={({ isActive }) =>
                  `transition-all duration-200 hover:text-gold-400 ${
                    isActive 
                      ? 'text-gold-400 border-b-2 border-gold-400 pb-1' 
                      : 'text-zinc-300 hover:text-white'
                  }`
                }
              >
                Home
              </NavLink>
              <NavLink
                to="/random"
                className={({ isActive }) =>
                  `transition-all duration-200 hover:text-gold-400 ${
                    isActive 
                      ? 'text-gold-400 border-b-2 border-gold-400 pb-1' 
                      : 'text-zinc-300 hover:text-white'
                  }`
                }
              >
                Random
              </NavLink>
              <NavLink
                to="/history"
                className={({ isActive }) =>
                  `transition-all duration-200 hover:text-gold-400 ${
                    isActive 
                      ? 'text-gold-400 border-b-2 border-gold-400 pb-1' 
                      : 'text-zinc-300 hover:text-white'
                  }`
                }
              >
                History
              </NavLink>
            </div>
          </div>

          {/* Utility Bar */}
          <div className="flex items-center gap-3">
            {/* Quick Search */}
            <div className="relative">
              {searchOpen ? (
                <div className="flex items-center gap-2 bg-zinc-800/50 rounded-xl px-3 py-2 border border-zinc-700 animate-in fade-in slide-in-from-right duration-200">
                  <Input
                    ref={searchRef}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleQuickGenerate()
                      if (e.key === 'Escape') setSearchOpen(false)
                    }}
                    placeholder="Quick topic search..."
                    className="w-48 h-8 bg-transparent border-none text-sm focus:ring-0 p-0"
                  />
                  <Button
                    size="sm"
                    onClick={handleQuickGenerate}
                    disabled={!searchQuery.trim()}
                    className="h-6 px-2 bg-gold-400 hover:bg-gold-500 text-black text-xs"
                  >
                    Go
                  </Button>
                  <button
                    onClick={() => setSearchOpen(false)}
                    className="text-zinc-400 hover:text-white p-1"
                  >
                    ✕
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setSearchOpen(true)}
                  className="p-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-white transition-all duration-200"
                  title="Quick search"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
              )}
            </div>

            {/* Style Selector */}
            <div className="hidden md:block">
              <StyleSelect value={currentStyle} onChange={setStyle} />
            </div>

            {/* Share Current Joke */}
            {currentJoke && currentJokeId && (
              <div className="hidden sm:block">
                <ShareButton jokeId={currentJokeId} jokeText={currentJoke} />
              </div>
            )}

            {/* Settings Menu */}
            <div className="relative" ref={settingsRef}>
              <button
                onClick={() => setSettingsOpen(!settingsOpen)}
                className="p-2 rounded-lg hover:bg-zinc-800/50 text-zinc-400 hover:text-white transition-all duration-200"
                title="Settings"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>

              {settingsOpen && (
                <div className="absolute top-full right-0 mt-2 w-64 bg-zinc-900 border border-zinc-700 rounded-xl shadow-xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
                  {/* Recent Topics */}
                  {recentTopics.length > 0 && (
                    <div className="p-3 border-b border-zinc-800">
                      <h4 className="text-xs font-medium text-zinc-400 mb-2 uppercase tracking-wide">Recent Topics</h4>
                      <div className="space-y-1">
                        {recentTopics.map((topic) => (
                          <button
                            key={topic}
                            onClick={() => {
                              navigate('/', { state: { query: topic, style: currentStyle } })
                              setSettingsOpen(false)
                            }}
                            className="block w-full text-left px-2 py-1 text-sm text-zinc-300 hover:bg-zinc-800 rounded transition-colors"
                          >
                            {topic}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Quick Actions */}
                  <div className="p-3">
                    <h4 className="text-xs font-medium text-zinc-400 mb-2 uppercase tracking-wide">Quick Actions</h4>
                    <div className="space-y-1">
                      <button
                        onClick={() => {
                          handleRandomJoke()
                          setSettingsOpen(false)
                        }}
                        className="flex items-center gap-2 w-full px-2 py-1.5 text-sm text-zinc-300 hover:bg-zinc-800 rounded transition-colors"
                      >
                        <span>🎲</span>
                        {' '}
                        Random Joke
                      </button>
                      <NavLink
                        to="/history"
                        onClick={() => setSettingsOpen(false)}
                        className="flex items-center gap-2 w-full px-2 py-1.5 text-sm text-zinc-300 hover:bg-zinc-800 rounded transition-colors"
                      >
                        <span>📚</span>
                        {' '}
                        View History
                      </NavLink>
                      <button
                        onClick={() => {
                          localStorage.removeItem('recentTopics')
                          setRecentTopics([])
                          setSettingsOpen(false)
                          toast.success('Recent topics cleared')
                        }}
                        className="flex items-center gap-2 w-full px-2 py-1.5 text-sm text-zinc-300 hover:bg-zinc-800 rounded transition-colors"
                      >
                        <span>🗑️</span>
                        {' '}
                        Clear Recent
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}