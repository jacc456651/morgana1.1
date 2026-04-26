export const STAGES = [
  { id: 1, name: 'Descubrir',  commands: ['sabueso'] },
  { id: 2, name: 'Analizar',   commands: ['analiza'] },
  { id: 3, name: 'Validar',    commands: ['compounder', 'consejo'] },
  { id: 4, name: 'Decidir',    commands: ['asignacion'] },
  { id: 5, name: 'Monitor',    commands: ['chequea'] },
]

export function computeStage(tickerAnalyses) {
  const ran = new Set(tickerAnalyses.map(a => a.command?.toLowerCase()))
  let currentStage = 1

  for (const s of STAGES) {
    const allDone = s.commands.every(c => ran.has(c))
    if (allDone) currentStage = s.id
  }

  const nextStage = STAGES.find(s => s.id === currentStage + 1)
  const pending = nextStage
    ? nextStage.commands.filter(c => !ran.has(c))
    : []

  return { stage: currentStage, completed: ran, pending }
}

export function buildWatchlist(analyses) {
  const byTicker = {}
  for (const a of analyses) {
    if (!byTicker[a.ticker]) byTicker[a.ticker] = []
    byTicker[a.ticker].push(a)
  }

  return Object.entries(byTicker)
    .map(([ticker, items]) => {
      const { stage, pending } = computeStage(items)
      const latest = items[0]
      return {
        ticker,
        stage,
        pending,
        score: latest?.score_final ?? null,
        decision: latest?.decision ?? null,
      }
    })
    .sort((a, b) => b.stage - a.stage || (b.score ?? 0) - (a.score ?? 0))
}
