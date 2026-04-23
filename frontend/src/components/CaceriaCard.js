import { Star, Copy, Check, AlertTriangle, Lightbulb } from 'lucide-react';

const tabColors = {
  'Descriptive': 'bg-teal-500/20 text-teal-400 border-teal-500/30',
  'Fundamental': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  'Technical': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  'All': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
};

const CaceriaCard = ({ caceria, isFavorite, onToggleFavorite, onCopyUrl, copied }) => {
  return (
    <div className="border border-white/[0.08] bg-[#111111] hover:border-white/20 transition-colors" data-testid={`caceria-card-${caceria.id}`}>
      <div className="flex items-start gap-4 p-5 md:p-6 border-b border-white/[0.06]">
        <div
          className="w-11 h-11 md:w-12 md:h-12 flex items-center justify-center font-mono font-bold text-sm md:text-base shrink-0 rounded-sm"
          style={{ backgroundColor: caceria.color + '18', color: caceria.color, border: `1px solid ${caceria.color}30` }}
        >
          {caceria.label}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 md:gap-3">
            <h3 className="font-heading text-lg md:text-xl text-[#FAFAFA] truncate">{caceria.name}</h3>
            <button
              onClick={onToggleFavorite}
              className="shrink-0 p-1 hover:bg-white/5 rounded transition-colors"
              data-testid={`favorite-btn-${caceria.id}`}
              aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
            >
              <Star
                size={16}
                className={isFavorite ? 'fill-[#C5A059] text-[#C5A059]' : 'text-[#737373] hover:text-[#C5A059]'}
              />
            </button>
          </div>
          <p className="text-sm text-[#A3A3A3] mt-0.5">{caceria.subtitle}</p>
          <p className="text-xs text-[#737373] mt-0.5 italic hidden md:block">{caceria.tagline}</p>
        </div>
      </div>

      <div className="p-5 md:p-6 space-y-5">
        <p className="text-sm text-[#A3A3A3] leading-relaxed">{caceria.description}</p>

        <div className="space-y-2">
          <h4 className="font-mono text-[10px] md:text-xs uppercase tracking-[0.2em] text-[#C5A059] font-bold">Filtros exactos</h4>
          <div className="space-y-0.5">
            {caceria.filters.map((f, i) => (
              <div key={i} className="flex flex-wrap md:flex-nowrap items-center gap-2 md:gap-3 py-1.5 px-3 bg-white/[0.02] border-l-2" style={{ borderColor: caceria.color + '40' }}>
                <span className={`text-[9px] md:text-[10px] px-1.5 md:px-2 py-0.5 rounded-sm border font-mono shrink-0 ${tabColors[f.tab] || tabColors['Fundamental']}`}>
                  {f.tab}
                </span>
                <span className="text-xs md:text-sm text-[#737373] font-mono flex-1 min-w-0">{f.filter}</span>
                <span className="text-xs md:text-sm text-[#FAFAFA] font-mono font-medium shrink-0">{f.value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="border border-white/[0.08] bg-white/[0.02] p-3 md:p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] md:text-xs font-mono text-[#C5A059] uppercase tracking-[0.15em]">URL directa</span>
            <button
              onClick={() => onCopyUrl(caceria.url, caceria.id)}
              className="flex items-center gap-1.5 text-[10px] md:text-xs font-mono px-2.5 md:px-3 py-1 md:py-1.5 bg-[#C5A059] text-black hover:bg-[#D4AF37] transition-colors rounded-sm"
              data-testid={`copy-url-${caceria.id}`}
            >
              {copied ? <Check size={11} /> : <Copy size={11} />}
              {copied ? 'Copiado' : 'Copiar'}
            </button>
          </div>
          <p className="text-[10px] md:text-xs text-[#737373] font-mono break-all leading-relaxed">{caceria.url}</p>
        </div>

        {caceria.interpretation && (
          <div>
            <h4 className="text-sm font-semibold text-[#FAFAFA] mb-1.5">Como interpretar los resultados</h4>
            <p className="text-sm text-[#A3A3A3] leading-relaxed">{caceria.interpretation}</p>
          </div>
        )}

        {caceria.pairs && (
          <div className="space-y-2">
            <h4 className="font-mono text-[10px] md:text-xs uppercase tracking-[0.2em] text-[#C5A059] font-bold">Pares clasicos MORGANA</h4>
            {caceria.pairs.map((p, i) => (
              <div key={i} className="flex items-center gap-3 py-1.5 px-3 bg-white/[0.02]">
                <span className="text-sm font-mono text-blue-400">LONG {p.long}</span>
                <span className="text-xs text-[#737373]">vs</span>
                <span className="text-sm font-mono text-red-400">SHORT {p.short}</span>
              </div>
            ))}
          </div>
        )}

        {caceria.tips?.map((tip, i) => (
          <div key={i} className="border-l-2 border-[#C5A059] pl-3 md:pl-4 py-2.5 md:py-3 bg-[#C5A059]/5">
            <div className="flex items-center gap-2 mb-1">
              <Lightbulb size={13} className="text-[#C5A059] shrink-0" />
              <strong className="text-sm text-[#FAFAFA]">{tip.title}</strong>
            </div>
            <p className="text-xs md:text-sm text-[#A3A3A3] leading-relaxed">{tip.text}</p>
          </div>
        ))}

        {caceria.warnings?.map((w, i) => (
          <div key={i} className={`border-l-2 pl-3 md:pl-4 py-2.5 md:py-3 ${w.type === 'danger' ? 'border-red-500 bg-red-500/5' : 'border-amber-500 bg-amber-500/5'}`}>
            <div className="flex items-center gap-2 mb-1">
              <AlertTriangle size={13} className={`shrink-0 ${w.type === 'danger' ? 'text-red-500' : 'text-amber-500'}`} />
              <strong className="text-sm text-[#FAFAFA]">{w.title}</strong>
            </div>
            <p className="text-xs md:text-sm text-[#A3A3A3] leading-relaxed">{w.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CaceriaCard;
