import ReactMarkdown from 'react-markdown'

function extractPillars(text) {
  const pillars = {}
  const re = /###\s+P(\d)[^|]+\|\s*Score:\s*(\d+(?:\.\d+)?)\/10/g
  let m
  while ((m = re.exec(text)) !== null) {
    pillars[`P${m[1]}`] = parseFloat(m[2])
  }
  return pillars
}

const PILLAR_LABELS = {
  P1: 'Moat Dinámico (25%)',
  P2: 'Finanzas Growth (15%)',
  P3: 'Motor de Crecimiento (25%)',
  P4: 'Management + Capital (25%)',
  P5: 'Contexto + Timing (10%)',
}

function PillarBar({ id, score }) {
  const pct = (score / 10) * 100
  const color = score >= 8 ? 'bg-emerald-500' : score >= 6 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs text-zinc-400 mb-1">
        <span>{id} — {PILLAR_LABELS[id]}</span>
        <span className="font-mono">{score}/10</span>
      </div>
      <div className="h-1.5 bg-zinc-800 rounded-full">
        <div className={`h-1.5 rounded-full ${color} transition-all`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function ReportView({ reporte, score, decision }) {
  if (!reporte) {
    return (
      <div className="p-6 text-zinc-600 text-sm">
        No hay reporte. Corre /analiza para generar uno.
      </div>
    )
  }

  const pillars = extractPillars(reporte)
  const hasPillars = Object.keys(pillars).length > 0

  return (
    <div className="p-4">
      {hasPillars && (
        <div className="mb-6 p-4 bg-zinc-900 rounded-xl border border-zinc-800">
          <div className="flex items-center gap-4 mb-4">
            <div className="text-4xl font-bold text-zinc-100">{score ?? '--'}/100</div>
            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
              decision === 'BUY' ? 'bg-emerald-900 text-emerald-300'
              : decision === 'AVOID' ? 'bg-red-900 text-red-300'
              : 'bg-yellow-900 text-yellow-300'
            }`}>
              {decision ?? 'N/A'}
            </div>
          </div>
          {['P1','P2','P3','P4','P5'].map(id =>
            pillars[id] != null && (
              <PillarBar key={id} id={id} score={pillars[id]} />
            )
          )}
        </div>
      )}

      <div className="prose prose-invert prose-sm max-w-none
        prose-headings:text-zinc-200 prose-p:text-zinc-300
        prose-strong:text-zinc-100 prose-code:text-violet-300
        prose-h2:text-lg prose-h3:text-base prose-h3:text-violet-300">
        <ReactMarkdown>{reporte}</ReactMarkdown>
      </div>
    </div>
  )
}
