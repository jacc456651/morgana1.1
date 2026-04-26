import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import LiveRunner from '../components/LiveRunner.jsx'

const CACERIAS_OPTS = [
  { id: 1, label: 'C1 — Quality Growth' },
  { id: 2, label: 'C2 — Deep Value' },
  { id: 3, label: 'C3 — GARP' },
  { id: 4, label: 'C4 — Insider Buying' },
  { id: 5, label: 'C5 — Momentum' },
  { id: 6, label: 'C6 — Turnaround' },
  { id: 7, label: 'C7 — Thematic' },
]

export default function Sabueso({ onTickerSelect }) {
  const [selectedCacerias, setSelectedCacerias] = useState([1, 5])
  const [runUrl, setRunUrl] = useState(null)
  const [results, setResults] = useState([])
  const navigate = useNavigate()

  const toggleCaceria = (id) => {
    setSelectedCacerias(prev =>
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]
    )
  }

  const startHunt = () => {
    if (selectedCacerias.length === 0 || runUrl) return
    setResults([])
    setRunUrl(`/api/sabueso?cacerias=${selectedCacerias.join(',')}`)
  }

  const handleDone = (event) => {
    setResults(event.results || [])
    setRunUrl(null)
  }

  return (
    <div className="p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-zinc-100 mb-1">Sabueso</h1>
        <p className="text-sm text-zinc-500">Screener sistemático — S&P500 + Nasdaq100</p>
      </div>

      <div className="p-4 bg-zinc-900 rounded-xl border border-zinc-800 mb-6">
        <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">
          Cacerías
        </div>
        <div className="flex flex-wrap gap-2 mb-4">
          {CACERIAS_OPTS.map(c => (
            <button
              key={c.id}
              onClick={() => toggleCaceria(c.id)}
              className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                selectedCacerias.includes(c.id)
                  ? 'border-violet-500 bg-violet-900/50 text-violet-300'
                  : 'border-zinc-700 text-zinc-500 hover:border-zinc-600 hover:text-zinc-400'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
        <button
          onClick={startHunt}
          disabled={!!runUrl || selectedCacerias.length === 0}
          className="px-5 py-2 bg-violet-700 hover:bg-violet-600 disabled:opacity-40 rounded text-sm text-white transition-colors"
        >
          {runUrl ? '⏳ Cazando...' : 'Cazar ahora'}
        </button>
      </div>

      {runUrl && (
        <div className="mb-6">
          <LiveRunner url={runUrl} onDone={handleDone} onError={() => setRunUrl(null)} />
        </div>
      )}

      {results.length > 0 && (
        <div>
          <div className="text-sm font-semibold text-zinc-400 mb-3">
            {results.length} presas encontradas
          </div>
          <div className="overflow-x-auto rounded-lg border border-zinc-800">
            <table className="w-full text-sm">
              <thead className="bg-zinc-900">
                <tr className="text-xs text-zinc-600 border-b border-zinc-800">
                  <th className="text-left py-2 px-3">Ticker</th>
                  <th className="text-left py-2 px-3">Cacería</th>
                  <th className="text-right py-2 px-3">Score</th>
                  <th className="text-right py-2 px-3">CAGR</th>
                  <th className="text-right py-2 px-3">GM</th>
                  <th className="text-right py-2 px-3">Mkt Cap B</th>
                  <th className="text-left py-2 px-3">Acción</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => (
                  <tr key={i} className="border-b border-zinc-800/50 hover:bg-zinc-900 transition-colors">
                    <td className="py-2 px-3 font-mono font-semibold text-violet-400">{r.Ticker}</td>
                    <td className="py-2 px-3 text-zinc-400 text-xs">C{r.Caceria}</td>
                    <td className="py-2 px-3 text-right text-zinc-300">{r.Score?.toFixed(1)}</td>
                    <td className="py-2 px-3 text-right text-zinc-300">{r.CAGR}</td>
                    <td className="py-2 px-3 text-right text-zinc-300">{r.Gross_Margin}</td>
                    <td className="py-2 px-3 text-right text-zinc-300">{r.Market_Cap_B}B</td>
                    <td className="py-2 px-3">
                      <button
                        onClick={() => { onTickerSelect?.(r.Ticker); navigate('/') }}
                        className="text-xs px-2 py-1 bg-violet-900/50 border border-violet-700/50 text-violet-400 rounded hover:bg-violet-900 transition-colors"
                      >
                        → /analiza
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
