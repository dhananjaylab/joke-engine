// FIX Phase-1: Removed `import heroImg from './assets/hero.png'`.
// hero.png does not exist in the assets directory, causing `vite build` to
// throw a module-not-found error on every production build.
// App.tsx is a Vite scaffold leftover — the app routes through main.tsx → Root.
// The file is kept for reference but the broken import is removed.

import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <section id="center">
        <div className="hero">
          {/* heroImg removed — file does not exist */}
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>
        <div>
          <h1>Get started</h1>
          <p>
            Edit <code>src/App.tsx</code> and save to test <code>HMR</code>
          </p>
        </div>
        <button
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Count is {count}
        </button>
      </section>
    </>
  )
}

export default App
