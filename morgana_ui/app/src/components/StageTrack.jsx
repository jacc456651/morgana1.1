import { STAGES } from '../utils/stages.js'

export default function StageTrack({ currentStage }) {
  return (
    <div className="flex items-center gap-1">
      {STAGES.map((s, i) => {
        const done = s.id <= currentStage
        const active = s.id === currentStage + 1
        return (
          <div key={s.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-colors ${
                done
                  ? 'bg-violet-600 border-violet-600 text-white'
                  : active
                  ? 'bg-transparent border-violet-400 text-violet-400'
                  : 'bg-transparent border-zinc-700 text-zinc-600'
              }`}>
                {done ? '✓' : s.id}
              </div>
              <span className={`text-xs mt-0.5 whitespace-nowrap ${
                done ? 'text-violet-400' : active ? 'text-zinc-400' : 'text-zinc-600'
              }`}>
                {s.name}
              </span>
            </div>
            {i < STAGES.length - 1 && (
              <div className={`w-8 h-0.5 mx-1 mb-4 ${
                s.id < currentStage ? 'bg-violet-600' : 'bg-zinc-800'
              }`} />
            )}
          </div>
        )
      })}
    </div>
  )
}
