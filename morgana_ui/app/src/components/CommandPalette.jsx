import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

const ALL_COMMANDS = [
  { id: 'analiza',    label: '/analiza',    desc: 'Análisis 5 pilares completo',       stage: 2 },
  { id: 'compounder', label: '/compounder', desc: 'Unit economics y SaaS metrics',     stage: 3 },
  { id: 'consejo',    label: '/consejo',    desc: 'Tesis falsificable + scorecard',    stage: 3 },
  { id: 'asignacion', label: '/asignacion', desc: 'Capital allocation decision',       stage: 4 },
  { id: 'chequea',    label: '/chequea',    desc: 'Actualiza con datos recientes',     stage: 5 },
  { id: 'sabueso',    label: '/sabueso',    desc: 'Screener — caza de oportunidades',  stage: 1 },
  { id: 'modelo',     label: '/modelo',     desc: 'Modelo DCF + escenarios',           stage: 4 },
]

const ACTOR_COMMANDS = [
  'goldman','morgan','jpmorgan','bridgewater','blackrock',
  'citadel','deshaw','twosigma','bain','vanguard'
].map(id => ({
  id,
  label: `/${id}`,
  desc: `Análisis ${id}`,
  isActor: true,
}))

export default function CommandPalette({ activeTicker, analyses, onClose, onTickerSelect, onRunCommand }) {
  const [query, setQuery] = useState('')
  const inputRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const ran = new Set(
    analyses
      .filter(a => a.ticker === activeTicker)
      .map(a => a.command?.toLowerCase())
  )

  const allOptions = [...ALL_COMMANDS, ...ACTOR_COMMANDS]

  const filtered = query
    ? allOptions.filter(c =>
        c.label.toLowerCase().includes(query.toLowerCase()) ||
        c.desc.toLowerCase().includes(query.toLowerCase())
      )
    : allOptions

  const tickerMatches = query.length >= 2
    ? [...new Set(analyses.map(a => a.ticker))]
        .filter(t => t.includes(query.toUpperCase()))
        .slice(0, 5)
    : []

  const handleSelect = (cmd) => {
    if (cmd.id === 'sabueso') {
      navigate('/sabueso')
      onClose()
      return
    }
    onRunCommand?.(cmd.id, activeTicker)
    onClose()
  }

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 flex items-start justify-center pt-24"
      onClick={onClose}
    >
      <div
        className="w-full max-w-xl bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 px-4 py-3 border-b border-zinc-800">
          <span className="text-zinc-500 text-sm">⌘</span>
          <input
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Escape' && onClose()}
            placeholder={activeTicker ? `Comando para ${activeTicker}...` : 'Buscar comando o ticker...'}
            className="flex-1 bg-transparent text-zinc-100 placeholder-zinc-600 text-sm outline-none"
          />
          {activeTicker && (
            <span className="text-xs px-2 py-0.5 bg-zinc-800 rounded text-zinc-400">
              {activeTicker}
            </span>
          )}
        </div>

        <div className="max-h-80 overflow-y-auto">
          {tickerMatches.length > 0 && (
            <div>
              <div className="px-3 py-1.5 text-xs text-zinc-600 uppercase tracking-wider">Tickers</div>
              {tickerMatches.map(t => (
                <button
                  key={t}
                  onClick={() => { onTickerSelect(t); navigate('/') }}
                  className="w-full flex items-center gap-3 px-4 py-2 hover:bg-zinc-800 text-left transition-colors"
                >
                  <span className="text-sm font-mono font-semibold text-zinc-200">{t}</span>
                  <span className="text-xs text-zinc-600">abrir dossier</span>
                </button>
              ))}
            </div>
          )}

          {filtered.length > 0 && (
            <div>
              <div className="px-3 py-1.5 text-xs text-zinc-600 uppercase tracking-wider">Comandos</div>
              {filtered.map(cmd => {
                const isDone = ran.has(cmd.id)
                return (
                  <button
                    key={cmd.id}
                    onClick={() => handleSelect(cmd)}
                    disabled={!activeTicker && cmd.id !== 'sabueso'}
                    className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-zinc-800 text-left disabled:opacity-40 transition-colors"
                  >
                    <span className="text-sm font-mono text-violet-400 w-28 flex-shrink-0">{cmd.label}</span>
                    <span className="text-xs text-zinc-400 flex-1">{cmd.desc}</span>
                    {isDone && <span className="text-xs text-emerald-600 flex-shrink-0">ya corrido</span>}
                    {!isDone && activeTicker && <span className="text-xs text-amber-600 flex-shrink-0">pendiente</span>}
                  </button>
                )
              })}
            </div>
          )}

          {filtered.length === 0 && tickerMatches.length === 0 && (
            <div className="px-4 py-6 text-center text-zinc-600 text-sm">
              Sin resultados para &ldquo;{query}&rdquo;
            </div>
          )}
        </div>

        <div className="px-4 py-2 border-t border-zinc-800 flex gap-4 text-xs text-zinc-600">
          <span>↑↓ navegar</span>
          <span>↵ seleccionar</span>
          <span>esc cerrar</span>
        </div>
      </div>
    </div>
  )
}
