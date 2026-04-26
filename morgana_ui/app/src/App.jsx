import { Routes, Route, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'

// Stub components — replaced in Tasks 5-12
const WatchlistStub = ({ onSelect }) => (
  <aside className="w-48 flex-shrink-0 bg-zinc-900 border-r border-zinc-800 flex flex-col">
    <div className="px-3 py-3 border-b border-zinc-800">
      <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Watchlist</span>
    </div>
    <div className="flex-1 flex items-center justify-center">
      <p className="text-xs text-zinc-600 px-3 text-center">Carga análisis para ver tickers</p>
    </div>
  </aside>
)

const DossierStub = ({ ticker }) => (
  <div className="flex items-center justify-center h-full">
    <div className="text-center">
      <div className="text-4xl mb-3">📊</div>
      <div className="text-zinc-500 text-sm">
        {ticker ? `Dossier: ${ticker}` : 'Selecciona un ticker'}
      </div>
      <div className="text-zinc-700 text-xs mt-2">Ctrl+K para buscar</div>
    </div>
  </div>
)

const SabuesoStub = () => (
  <div className="p-8">
    <h1 className="text-2xl font-bold text-zinc-100 mb-2">Sabueso</h1>
    <p className="text-zinc-500 text-sm">Screener — próximamente</p>
  </div>
)

export default function App() {
  const [activeTicker, setActiveTicker] = useState(null)
  const [analyses, setAnalyses] = useState([])
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
        // CommandPalette wired in Task 10
        console.log('Ctrl+K — palette coming in Task 10')
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
    <div className="flex h-screen overflow-hidden bg-zinc-950">
      <WatchlistStub onSelect={setActiveTicker} />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<DossierStub ticker={activeTicker} />} />
          <Route path="/sabueso" element={<SabuesoStub />} />
        </Routes>
      </main>
    </div>
  )
}
