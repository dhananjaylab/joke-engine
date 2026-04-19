interface StyleSelectProps {
  value: string
  onChange: (style: string) => void
}

const STYLES = [
  // Classic Styles
  { value: 'sarcastic', label: '😏 Sarcastic' },
  { value: 'witty', label: '🧠 Witty' },
  { value: 'dad', label: '👨 Dad Jokes' },
  { value: 'roast', label: '🔥 Roast' },
  { value: 'observational', label: '👀 Observational' },
  { value: 'dark', label: '🖤 Dark' },
  
  // Modern Styles
  { value: 'gen-z', label: '📱 Gen Z' },
  { value: 'millennial', label: '🥑 Millennial' },
  { value: 'boomer', label: '📰 Boomer' },
  { value: 'meme', label: '🐸 Meme' },
  { value: 'tiktok', label: '🎵 TikTok' },
  { value: 'twitter', label: '🐦 Twitter' },
  
  // Character Styles
  { value: 'karen', label: '💁‍♀️ Karen' },
  { value: 'chad', label: '💪 Chad' },
  { value: 'nerd', label: '🤓 Nerd' },
  { value: 'hipster', label: '🎨 Hipster' },
  { value: 'influencer', label: '✨ Influencer' },
  { value: 'corporate', label: '💼 Corporate' },
  
  // Comedy Styles
  { value: 'absurd', label: '🤪 Absurd' },
  { value: 'puns', label: '🎭 Puns' },
  { value: 'self-deprecating', label: '😅 Self-Deprecating' },
  { value: 'wholesome', label: '🌟 Wholesome' },
  { value: 'cringe', label: '😬 Cringe' },
  { value: 'deadpan', label: '😐 Deadpan' },
  
  // Pop Culture
  { value: 'netflix', label: '📺 Netflix' },
  { value: 'gaming', label: '🎮 Gaming' },
  { value: 'crypto', label: '₿ Crypto Bro' },
  { value: 'fitness', label: '💪 Fitness' },
  { value: 'foodie', label: '🍕 Foodie' },
  { value: 'travel', label: '✈️ Travel' },
]

export function StyleSelect({ value, onChange }: StyleSelectProps) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-11 sm:h-12 px-3 sm:px-4 pr-10 rounded-xl border border-zinc-700 bg-zinc-900 text-white text-sm sm:text-base appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-gold-400/50 transition-all hover:border-zinc-600 hover:bg-zinc-800"
        style={{ maxHeight: '300px' }}
      >
        <optgroup label="🎭 Classic Comedy">
          {STYLES.slice(0, 6).map((style) => (
            <option key={style.value} value={style.value} className="bg-zinc-900 text-white py-2">
              {style.label}
            </option>
          ))}
        </optgroup>
        
        <optgroup label="📱 Modern Vibes">
          {STYLES.slice(6, 12).map((style) => (
            <option key={style.value} value={style.value} className="bg-zinc-900 text-white py-2">
              {style.label}
            </option>
          ))}
        </optgroup>
        
        <optgroup label="👥 Character Types">
          {STYLES.slice(12, 18).map((style) => (
            <option key={style.value} value={style.value} className="bg-zinc-900 text-white py-2">
              {style.label}
            </option>
          ))}
        </optgroup>
        
        <optgroup label="🎪 Comedy Styles">
          {STYLES.slice(18, 24).map((style) => (
            <option key={style.value} value={style.value} className="bg-zinc-900 text-white py-2">
              {style.label}
            </option>
          ))}
        </optgroup>
        
        <optgroup label="🌟 Pop Culture">
          {STYLES.slice(24).map((style) => (
            <option key={style.value} value={style.value} className="bg-zinc-900 text-white py-2">
              {style.label}
            </option>
          ))}
        </optgroup>
      </select>
      <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg className="w-4 h-4 sm:w-5 sm:h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  )
}
