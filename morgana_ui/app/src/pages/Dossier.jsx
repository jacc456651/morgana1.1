import { useState, useEffect } from 'react'
import StageTrack from '../components/StageTrack.jsx'
import DossierTabs from '../components/DossierTabs.jsx'
import LiveRunner from '../components/LiveRunner.jsx'
import ReportView from '../components/ReportView.jsx'
import ActorsGrid from '../components/ActorsGrid.jsx'
import { computeStage } from '../utils/stages.js'

export default function Dossier({ ticker, analyses, onAnalysisComplete }) {
  const [activeTab, setActiveTab] = useState('overview')
  const [runningUrl, setRunningUrl] = useState(null)
  const [tickerAnalyses, setTickerAnalyses] = useState([])

  useEffect(() => {
    if (!ticker) return
    fetch(`/api/analyses/${ticker}`)
      .then(r => r.json())
      .then(({ data }) => setTickerAnalyses(data || []))
      .catch(() => {})
  }, [ticker])

  if (!ticker) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-4xl mb-3">📊</div>
          <div className="text-zinc-500 text-sm">
            Selecciona un ticker en el sidebar o usa{' '}
            <kbd className="px-1.5 py-0.5 bg-zinc-800 rounded text-xs">Ctrl+K</kbd>
          </div>
        </div>
      </div>
    )
  }

  const { stage, completed, pending } = computeStage(tickerAnalyses)
  const latest = tickerAnalyses[0]
  const latestAnaliza = tickerAnalyses.find(a => a.command === 'analiza')

  const handleRunCommand = (command) => {
    setRunningUrl(`/api/analyze?ticker=${ticker}&command=${command}`)
    setActiveTab('analisis')
  }

  const handleDone = (event) => {
    setRunningUrl(null)
    onAnalysisComplete?.({ ticker, command: 'analiza', ...event })
    fetch(`/api/analyses/${ticker}`)
      .then(r => r.json())
      .then(({ data }) => setTickerAnalyses(data || []))
      .catch(() => {})
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-6 py-4 border-b border-zinc-800">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-zinc-100">{ticker}</h1>
            {latest && (
              <div className="flex items-center gap-3 mt-1">
                <span className="text-3xl font-bold text-zinc-100">
                  {latest.score_final ?? '--'}/100
                </span>
                <span className={`px-2 py-0.5 rounded text-sm font-semibold ${
                  latest.decision === 'BUY' ? 'bg-emerald-900 text-emerald-300'
                  : latest.decision === 'AVOID' ? 'bg-red-900 text-red-300'
                  : 'bg-yellow-900 text-yellow-300'
                }`}>
                  {latest.decision}
                </span>
                <span className="text-xs text-zinc-600">{latest.classification}</span>
              </div>
            )}
          </div>

          <div className="flex flex-col items-end gap-2 flex-shrink-0">
            <StageTrack currentStage={stage} />
            {pending.length > 0 && (
              <div className="flex items-center gap-2 flex-wrap justify-end">
                <span className="text-xs text-zinc-600">Faltan:</span>
                {pending.map(cmd => (
                  <button
                    key={cmd}
                    onClick={() => handleRunCommand(cmd)}
                    className="text-xs px-2 py-0.5 bg-amber-900/50 border border-amber-700/50 text-amber-400 rounded hover:bg-amber-900 transition-colors"
                  >
                    /{cmd}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <DossierTabs activeTab={activeTab} onTabChange={setActiveTab} completed={completed} />

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {runningUrl && (
          <div className="px-6 py-4 border-b border-zinc-800 bg-zinc-900/50">
            <LiveRunner url={runningUrl} onDone={handleDone} onError={() => setRunningUrl(null)} />
          </div>
        )}

        {activeTab === 'overview' && (
          <div className="p-6">
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
                <div className="text-xs text-zinc-600 mb-1">Último análisis</div>
                <div className="text-sm text-zinc-300">
                  {latest?.created_at
                    ? new Date(latest.created_at).toLocaleDateString('es')
                    : 'N/A'}
                </div>
              </div>
              <div className="p-4 bg-zinc-900 rounded-lg border border-zinc-800">
                <div className="text-xs text-zinc-600 mb-1">Análisis realizados</div>
                <div className="text-sm text-zinc-300">{tickerAnalyses.length}</div>
              </div>
            </div>
            {latestAnaliza ? (
              <ReportView
                reporte={latestAnaliza.reporte}
                score={latestAnaliza.score_final}
                decision={latestAnaliza.decision}
              />
            ) : (
              <div className="text-center py-12">
                <div className="text-zinc-600 text-sm mb-3">Sin análisis completo aún</div>
                <button
                  onClick={() => handleRunCommand('analiza')}
                  className="px-4 py-2 bg-violet-700 hover:bg-violet-600 rounded text-sm text-white transition-colors"
                >
                  Correr /analiza
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'analisis' && (
          <ReportView
            reporte={latestAnaliza?.reporte}
            score={latestAnaliza?.score_final}
            decision={latestAnaliza?.decision}
          />
        )}

        {activeTab === 'actores' && <ActorsGrid ticker={ticker} />}

        {activeTab === 'historia' && (
          <div className="p-6">
            <h3 className="text-sm font-semibold text-zinc-400 mb-4">Historial de análisis</h3>
            {tickerAnalyses.length === 0 && (
              <p className="text-zinc-600 text-sm">Sin análisis previos.</p>
            )}
            {tickerAnalyses.map((a, i) => (
              <div key={a.id ?? i} className="mb-3 p-3 bg-zinc-900 rounded-lg border border-zinc-800">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-zinc-300 font-mono">{a.command}</span>
                  <div className="flex items-center gap-2">
                    {a.score_final != null && (
                      <span className="text-sm font-mono text-zinc-200">{a.score_final}/100</span>
                    )}
                    <span className={`text-xs font-medium ${
                      a.decision === 'BUY' ? 'text-emerald-400'
                      : a.decision === 'AVOID' ? 'text-red-400'
                      : 'text-yellow-400'
                    }`}>{a.decision}</span>
                  </div>
                </div>
                <div className="text-xs text-zinc-600 mt-1">
                  {new Date(a.created_at).toLocaleString('es')}
                </div>
              </div>
            ))}
          </div>
        )}

        {(activeTab === 'unitec' || activeTab === 'tesis' || activeTab === 'modelo') && (
          <div className="p-6 text-center py-12">
            <div className="text-zinc-600 text-sm mb-2">Tab pendiente</div>
            <button
              onClick={() => handleRunCommand(
                activeTab === 'unitec' ? 'compounder'
                : activeTab === 'tesis' ? 'consejo'
                : 'modelo'
              )}
              className="text-xs px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 rounded text-zinc-400 transition-colors"
            >
              Correr /{activeTab === 'unitec' ? 'compounder' : activeTab === 'tesis' ? 'consejo' : 'modelo'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
