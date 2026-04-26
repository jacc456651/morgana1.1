import { useState } from 'react'
import LiveRunner from './LiveRunner.jsx'

const ACTORS = [
  { id: 'goldman',     label: 'Goldman Sachs',   icon: '🏦' },
  { id: 'morgan',      label: 'Morgan Stanley',  icon: '🏦' },
  { id: 'jpmorgan',    label: 'J.P. Morgan',     icon: '🏦' },
  { id: 'bridgewater', label: 'Bridgewater',     icon: '🌊' },
  { id: 'blackrock',   label: 'BlackRock',       icon: '🪨' },
  { id: 'citadel',     label: 'Citadel',         icon: '🏰' },
  { id: 'deshaw',      label: 'D.E. Shaw',       icon: '⚙️' },
  { id: 'twosigma',    label: 'Two Sigma',       icon: '∑' },
  { id: 'bain',        label: 'Bain Capital',    icon: '📊' },
  { id: 'vanguard',    label: 'Vanguard',        icon: '⛵' },
]

export default function ActorsGrid({ ticker }) {
  const [running, setRunning] = useState(null)
  const [results, setResults] = useState({})
  const [expanded, setExpanded] = useState(null)

  const runActor = (actorId) => {
    if (!ticker || running) return
    setRunning(actorId)
    setExpanded(actorId)
  }

  const handleDone = (actorId) => (event) => {
    setResults(prev => ({ ...prev, [actorId]: event }))
    setRunning(null)
  }

  const runAll = () => {
    const pending = ACTORS.filter(a => !results[a.id])
    if (pending.length > 0 && !running) runActor(pending[0].id)
  }

  if (!ticker) {
    return <div className="p-4 text-zinc-600 text-sm">Selecciona un ticker.</div>
  }

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-zinc-400">
          {Object.keys(results).length}/10 actores corridos
        </h3>
        <button
          onClick={runAll}
          disabled={!!running}
          className="text-xs px-3 py-1 bg-zinc-800 hover:bg-zinc-700 rounded text-zinc-300 disabled:opacity-40 transition-colors"
        >
          Correr todos
        </button>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-4">
        {ACTORS.map(actor => {
          const done = !!results[actor.id]
          const isRunning = running === actor.id
          return (
            <button
              key={actor.id}
              onClick={() => {
                if (done) setExpanded(expanded === actor.id ? null : actor.id)
                else runActor(actor.id)
              }}
              disabled={isRunning || (!!running && running !== actor.id)}
              className={`flex items-center gap-2 p-3 rounded-lg border text-left transition-colors ${
                done
                  ? 'border-emerald-800 bg-emerald-950/30 hover:bg-emerald-950/50'
                  : 'border-zinc-800 bg-zinc-900 hover:bg-zinc-800'
              } disabled:opacity-40`}
            >
              <span className="text-lg">{actor.icon}</span>
              <div className="min-w-0">
                <div className="text-xs font-medium text-zinc-200 truncate">{actor.label}</div>
                <div className="text-xs text-zinc-600">
                  {isRunning ? '⏳ corriendo...' : done ? '✓ completado' : 'clic para correr'}
                </div>
              </div>
            </button>
          )
        })}
      </div>

      {expanded && running === expanded && (
        <LiveRunner
          url={`/api/actor?ticker=${ticker}&actor=${expanded}`}
          onDone={handleDone(expanded)}
          onError={() => setRunning(null)}
        />
      )}

      {expanded && results[expanded] && (
        <div className="mt-4 p-4 bg-zinc-900 rounded-lg border border-zinc-800">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-zinc-300">
              {ACTORS.find(a => a.id === expanded)?.label}
            </h4>
            <button
              onClick={() => setExpanded(null)}
              className="text-xs text-zinc-600 hover:text-zinc-400"
            >
              cerrar
            </button>
          </div>
          <pre className="whitespace-pre-wrap text-xs text-zinc-300 font-sans leading-relaxed">
            {results[expanded].reporte}
          </pre>
        </div>
      )}
    </div>
  )
}
