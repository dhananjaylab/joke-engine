import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Root from './layouts/Root'
import './index.css'

const Home = React.lazy(() => import('./pages/Home'))
const History = React.lazy(() => import('./pages/History'))
const Battle = React.lazy(() => import('./pages/Battle'))
const Heckle = React.lazy(() => import('./pages/Heckle'))
const JokeDetail = React.lazy(() => import('./pages/JokeDetail'))
const Profile = React.lazy(() => import('./pages/Profile'))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 1000 * 60 * 2 },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Root />}>
            <Route
              index
              element={
                <React.Suspense fallback={null}>
                  <Home />
                </React.Suspense>
              }
            />
            <Route
              path="history"
              element={
                <React.Suspense fallback={null}>
                  <History />
                </React.Suspense>
              }
            />
            <Route
              path="battle"
              element={
                <React.Suspense fallback={null}>
                  <Battle />
                </React.Suspense>
              }
            />
            <Route
              path="heckle"
              element={
                <React.Suspense fallback={null}>
                  <Heckle />
                </React.Suspense>
              }
            />
            <Route
              path="joke/:id"
              element={
                <React.Suspense fallback={null}>
                  <JokeDetail />
                </React.Suspense>
              }
            />
            <Route
              path="profile"
              element={
                <React.Suspense fallback={null}>
                  <Profile />
                </React.Suspense>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)

// Register service worker for PWA functionality
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}
