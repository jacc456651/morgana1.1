import { useNavigate } from 'react-router-dom'
import { buildWatchlist, STAGES } from '../utils/stages.js'

const DECISION_COLOR = {
  BUY: 'text-emerald-400',
  HOLD: 'text-yellow-400',
  AVOID: 'text-red-400',
}

export default function Watchlist({ analyses, activeTicker, onSelect }) {
  const navigate = useNavigate()
  const tickers = buildWatchlist(analyses)

  return (
    <aside className="w-48 flex-shrink-0 bg-zinc-900 border-r border-zinc-800 flex flex-col overflow-hidden">
      <div className="px-3 py-3 border-b border-zinc-800">
        <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">
          Watchlist
        </span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {tickers.length === 0 && (
          <p className="px-3 py-4 text-xs text-zinc-600">
            Sin tickers. Corre /sabueso para empezar.
          </p>
        )}
        {tickers.map(({ ticker, stage, score, decision, pending }) => (
          <button
            key={ticker}
            onClick={() => { onSelect(ticker); navigate('/') }}
            className={`w-full text-left px-3 py-2.5 border-b border-zinc-800/50 hover:bg-zinc-800 transition-colors ${
              activeTicker === ticker ? 'bg-zinc-800 border-l-2 border-l-violet-500' : ''
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-semibold text-zinc-100">{ticker}</span>
              {score !== null && (
                <span className="text-xs text-zinc-400">{Math.round(score)}</span>
              )}
            </div>
            <div className="w-full h-1 bg-zinc-800 rounded-full mb-1">
              <div
                className="h-1 bg-violet-500 rounded-full transition-all"
                style={{ width: `${(stage / 5) * 100}%` }}
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-500">
                {STAGES[stage - 1]?.name ?? 'Monitor'}
              </span>
              {decision && (
                <span className={`text-xs font-medium ${DECISION_COLOR[decision] ?? 'text-zinc-400'}`}>
                  {decision}
                </span>
              )}
            </div>
            {pending.length > 0 && (
              <div className="mt-1 text-xs text-amber-500/70">
                +{pending.length} pendiente{pending.length > 1 ? 's' : ''}
              </div>
            )}
          </button>
        ))}
      </div>

      <div className="p-2 border-t border-zinc-800">
        <button
          onClick={() => navigate('/sabueso')}
          className="w-full text-xs py-1.5 px-2 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 transition-colors"
        >
          /sabueso
        </button>
      </div>
    </aside>
  )
}
