import { Routes, Route, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Watchlist from './components/Watchlist.jsx'
import CommandPalette from './components/CommandPalette.jsx'
import Dossier from './pages/Dossier.jsx'
import Sabueso from './pages/Sabueso.jsx'

export default function App() {
  const [activeTicker, setActiveTicker] = useState(null)
  const [analyses, setAnalyses] = useState([])
  const [paletteOpen, setPaletteOpen] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetch('/api/analyses')
      .then(r => r.json())
      .then(({ data }) => setAnalyses(data || []))
      .catch(() => {})
  }, [])

  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setPaletteOpen(p => !p)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const handleAnalysisComplete = (data) => {
    setAnalyses(prev => [data, ...prev])
  }

  return (
    <div className="flex h-screen overflow-hidden bg-zinc-950">
      <Watchlist
        analyses={analyses}
        activeTicker={activeTicker}
        onSelect={setActiveTicker}
      />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={
            <Dossier
              ticker={activeTicker}
              analyses={analyses}
              onAnalysisComplete={handleAnalysisComplete}
            />
          } />
          <Route path="/sabueso" element={
            <Sabueso onTickerSelect={(t) => { setActiveTicker(t); navigate('/') }} />
          } />
        </Routes>
      </main>
      {paletteOpen && (
        <CommandPalette
          activeTicker={activeTicker}
          analyses={analyses}
          onClose={() => setPaletteOpen(false)}
          onTickerSelect={(t) => { setActiveTicker(t); setPaletteOpen(false) }}
          onRunCommand={(cmd, ticker) => {
            setPaletteOpen(false)
            // The Dossier page handles run commands internally via its own state
            // For now, just navigate to / — Dossier will be active
            navigate('/')
          }}
        />
      )}
    </div>
  )
}
