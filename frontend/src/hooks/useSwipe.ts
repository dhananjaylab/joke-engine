import { useRef } from 'react'
import { useDrag } from '@use-gesture/react'

interface SwipeOptions {
  onSwipeRight?: () => void
  onSwipeLeft?: () => void
  threshold?: number
}

export function useSwipe({ onSwipeRight, onSwipeLeft, threshold = 0.35 }: SwipeOptions) {
  const ref = useRef<HTMLDivElement>(null)

  const bind = useDrag(({ movement: [mx], last }) => {
    const el = ref.current
    if (!el) return

    const pct = Math.abs(mx) / window.innerWidth

    if (!last) {
      el.style.transform = `translateX(${mx}px) rotate(${mx * 0.04}deg)`
      el.style.opacity = String(1 - pct * 0.4)
    } else {
      if (mx > window.innerWidth * threshold) {
        el.style.transition = 'transform 0.3s ease, opacity 0.3s ease'
        el.style.transform = 'translateX(100vw) rotate(15deg)'
        setTimeout(() => {
          if (el) { el.style.transform = ''; el.style.opacity = '1'; el.style.transition = '' }
          onSwipeRight?.()
        }, 320)
      } else if (mx < -window.innerWidth * threshold) {
        el.style.transition = 'transform 0.3s ease, opacity 0.3s ease'
        el.style.transform = 'translateX(-100vw) rotate(-15deg)'
        setTimeout(() => {
          if (el) { el.style.transform = ''; el.style.opacity = '1'; el.style.transition = '' }
          onSwipeLeft?.()
        }, 320)
      } else {
        el.style.transition = 'transform 0.2s ease, opacity 0.2s ease'
        el.style.transform = ''
        el.style.opacity = '1'
        setTimeout(() => { if (el) el.style.transition = '' }, 200)
      }
    }
  }, { filterTaps: true, axis: 'x' })

  return { ref, bind }
}
