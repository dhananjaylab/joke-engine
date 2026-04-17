import { useProfileStore } from '@/store/profileStore'

export default function Profile() {
  const { xp, streak, rank } = useProfileStore()

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Profile Header */}
      <div className="bg-gradient-to-br from-zinc-900 to-zinc-900/50 border border-zinc-800 rounded-2xl p-8 text-center">
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 mx-auto mb-4 flex items-center justify-center">
          <svg className="w-12 h-12 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-white mb-2">Comedy Enthusiast</h1>
        <div className="text-gold-400 font-semibold">{rank}</div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6 text-center">
          <div className="text-3xl font-bold text-gold-400 mb-2">{xp}</div>
          <div className="text-sm text-zinc-400">Total XP</div>
        </div>
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6 text-center">
          <div className="text-3xl font-bold text-orange-400 mb-2">{streak}</div>
          <div className="text-sm text-zinc-400">Day Streak 🔥</div>
        </div>
      </div>

      {/* Achievements */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6">
        <h2 className="text-lg font-bold text-white mb-4">Achievements</h2>
        <div className="grid grid-cols-3 gap-4">
          {[
            { icon: '🎭', label: 'First Joke', unlocked: true },
            { icon: '🔥', label: '7 Day Streak', unlocked: true },
            { icon: '⭐', label: '100 XP', unlocked: true },
            { icon: '🏆', label: 'Top Rated', unlocked: false },
            { icon: '💎', label: 'Premium', unlocked: false },
            { icon: '🌟', label: 'Legend', unlocked: false },
          ].map((achievement, i) => (
            <div
              key={i}
              className={`aspect-square rounded-xl flex flex-col items-center justify-center gap-2 ${
                achievement.unlocked
                  ? 'bg-gold-400/10 border border-gold-400/30'
                  : 'bg-zinc-800/30 border border-zinc-700/30 opacity-50'
              }`}
            >
              <div className="text-3xl">{achievement.icon}</div>
              <div className="text-xs text-center text-zinc-400">{achievement.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Settings */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6 space-y-4">
        <h2 className="text-lg font-bold text-white mb-4">Settings</h2>
        <button className="w-full text-left px-4 py-3 rounded-xl bg-zinc-800/50 hover:bg-zinc-800 transition-colors text-white">
          <div className="flex items-center justify-between">
            <span>Notifications</span>
            <svg className="w-5 h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>
        <button className="w-full text-left px-4 py-3 rounded-xl bg-zinc-800/50 hover:bg-zinc-800 transition-colors text-white">
          <div className="flex items-center justify-between">
            <span>Language Preferences</span>
            <svg className="w-5 h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>
        <button className="w-full text-left px-4 py-3 rounded-xl bg-zinc-800/50 hover:bg-zinc-800 transition-colors text-white">
          <div className="flex items-center justify-between">
            <span>Privacy & Data</span>
            <svg className="w-5 h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>
      </div>
    </div>
  )
}
