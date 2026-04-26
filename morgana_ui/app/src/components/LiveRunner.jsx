import { useState, useEffect, useRef } from 'react'

const AGENT_COLORS = {
  scout:      'text-violet-400',
  researcher: 'text-purple-400',
  boss:       'text-blue-400',
  save:       'text-emerald-400',
}

const AGENT_LABELS = {
  scout:      'Scout — recolectando datos',
  researcher: 'Researcher — contexto web',
  boss:       'Boss — análisis 5 pilares',
  save:       'Save — guardando',
}

const ANALIZA_STEPS = ['scout', 'researcher', 'boss', 'save']

export default function LiveRunner({ url, onDone, onError }) {
  const [steps, setSteps] = useState({})
  const [logs, setLogs] = useState([])
  const [status, setStatus] = useState('connecting')
  const [result, setResult] = useState(null)
  const logsEndRef = useRef(null)
  const esRef = useRef(null)

  useEffect(() => {
    if (!url) return
    setSteps({})
    setLogs([])
    setStatus('connecting')
    setResult(null)

    const es = new EventSource(url)
    esRef.current = es

    es.onopen = () => setStatus('running')

    es.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data)

        if (event.type === 'step') {
          setSteps(prev => ({
            ...prev,
            [event.agent]: { status: event.status, elapsed: event.elapsed },
          }))
          if (event.status === 'running') {
            setLogs(prev => [...prev, {
              agent: event.agent,
              text: `${AGENT_LABELS[event.agent] ?? event.agent}...`,
              ts: Date.now(),
            }])
          }
        }

        if (event.type === 'log') {
          setLogs(prev => [...prev, { agent: event.agent, text: event.text, ts: Date.now() }])
        }

        if (event.type === 'done') {
          setStatus('done')
          setResult(event)
          es.close()
          onDone?.(event)
        }

        if (event.type === 'error') {
          setStatus('error')
          setLogs(prev => [...prev, { agent: 'error', text: event.message, ts: Date.now() }])
          es.close()
          onError?.(event.message)
        }
      } catch {}
    }

    es.onerror = () => {
      if (status !== 'done') {
        setStatus('error')
        es.close()
      }
    }

    return () => es.close()
  }, [url])

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const agentKeys = Object.keys(steps).length > 0
    ? Object.keys(steps)
    : ANALIZA_STEPS

  if (status === 'connecting') {
    return <div className="py-4 text-zinc-500 text-sm">Conectando...</div>
  }

  return (
    <div className="flex gap-4 mt-4">
      {/* Stepper */}
      <div className="w-52 flex-shrink-0">
        {agentKeys.map(agent => {
          const s = steps[agent]
          const st = s?.status ?? 'pending'
          return (
            <div key={agent} className="flex items-start gap-2 mb-3">
              <div className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center text-xs flex-shrink-0 ${
                st === 'done' ? 'bg-emerald-600 text-white'
                : st === 'running' ? 'bg-blue-600 text-white animate-pulse'
                : 'bg-zinc-800 text-zinc-600'
              }`}>
                {st === 'done' ? '✓' : st === 'running' ? '⏳' : '○'}
              </div>
              <div>
                <div className={`text-sm ${AGENT_COLORS[agent] ?? 'text-zinc-300'}`}>
                  {AGENT_LABELS[agent] ?? agent}
                </div>
                {s?.elapsed != null && (
                  <div className="text-xs text-zinc-600">{s.elapsed}s</div>
                )}
              </div>
            </div>
          )
        })}

        {status === 'done' && result && (
          <div className="mt-4 p-3 bg-zinc-800 rounded-lg">
            <div className="text-2xl font-bold text-zinc-100">
              {result.score ?? '--'}/100
            </div>
            <div className={`text-sm font-semibold mt-1 ${
              result.decision === 'BUY' ? 'text-emerald-400'
              : result.decision === 'AVOID' ? 'text-red-400'
              : 'text-yellow-400'
            }`}>
              {result.decision ?? 'N/A'}
            </div>
            <div className="text-xs text-zinc-600 mt-1">{result.elapsed}s total</div>
          </div>
        )}

        {status === 'error' && (
          <div className="mt-2 p-2 bg-red-950 rounded text-xs text-red-400">
            Error en análisis
          </div>
        )}
      </div>

      {/* Live log */}
      <div className="flex-1 bg-zinc-900 rounded-lg p-3 font-mono text-xs overflow-y-auto max-h-64">
        {logs.map((log, i) => (
          <div key={i} className={`mb-0.5 ${AGENT_COLORS[log.agent] ?? 'text-zinc-400'}`}>
            <span className="text-zinc-600 mr-2">[{log.agent}]</span>
            {log.text}
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </div>
  )
}
