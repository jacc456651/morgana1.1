const TABS = [
  { id: 'overview',   label: 'Overview',    required: 'analiza' },
  { id: 'analisis',   label: 'Análisis',    required: 'analiza' },
  { id: 'unitec',     label: 'Unit Econ.',  required: 'compounder' },
  { id: 'actores',    label: 'Actores',     required: null },
  { id: 'tesis',      label: 'Tesis',       required: 'consejo' },
  { id: 'historia',   label: 'Historia',    required: null },
  { id: 'modelo',     label: 'Modelo',      required: 'modelo' },
]

export default function DossierTabs({ activeTab, onTabChange, completed = new Set() }) {
  return (
    <div className="flex gap-0.5 border-b border-zinc-800 px-4">
      {TABS.map(tab => {
        const done = tab.required ? completed.has(tab.required) : true
        const isActive = activeTab === tab.id
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-3 py-2 text-sm border-b-2 transition-colors -mb-px ${
              isActive
                ? 'border-violet-500 text-violet-400'
                : 'border-transparent text-zinc-500 hover:text-zinc-300'
            }`}
          >
            {tab.label}
            {tab.required && (
              <span className={`ml-1 text-xs ${done ? 'text-emerald-500' : 'text-zinc-700'}`}>
                {done ? '✓' : '●'}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
