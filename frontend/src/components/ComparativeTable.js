const ComparativeTable = ({ cacerias }) => {
  return (
    <div className="overflow-x-auto -mx-4 md:mx-0" data-testid="comparative-table">
      <table className="w-full text-sm min-w-[800px]">
        <thead>
          <tr className="border-b border-white/10">
            <th className="text-left p-2.5 md:p-3 font-mono text-[10px] md:text-xs text-[#C5A059] uppercase tracking-[0.15em]">#</th>
            <th className="text-left p-2.5 md:p-3 font-mono text-[10px] md:text-xs text-[#C5A059] uppercase tracking-[0.15em]">Caceria</th>
            <th className="text-left p-2.5 md:p-3 font-mono text-[10px] md:text-xs text-[#C5A059] uppercase tracking-[0.15em]">Perfil</th>
            <th className="text-left p-2.5 md:p-3 font-mono text-[10px] md:text-xs text-[#C5A059] uppercase tracking-[0.15em]">Exchange</th>
            <th className="text-left p-2.5 md:p-3 font-mono text-[10px] md:text-xs text-[#C5A059] uppercase tracking-[0.15em]">Market Cap</th>
            <th className="text-left p-2.5 md:p-3 font-mono text-[10px] md:text-xs text-[#C5A059] uppercase tracking-[0.15em]">Objetivo</th>
            <th className="text-left p-2.5 md:p-3 font-mono text-[10px] md:text-xs text-[#C5A059] uppercase tracking-[0.15em]">Filtros clave</th>
          </tr>
        </thead>
        <tbody>
          {cacerias.map((c) => (
            <tr key={c.id} className="border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors" data-testid={`table-row-${c.id}`}>
              <td className="p-2.5 md:p-3">
                <span className="font-mono font-bold text-sm" style={{ color: c.color }}>{c.label}</span>
              </td>
              <td className="p-2.5 md:p-3">
                <span className="font-heading text-[#FAFAFA] text-sm">{c.name}</span>
                <span className="block text-[10px] text-[#737373] mt-0.5">{c.subtitle}</span>
              </td>
              <td className="p-2.5 md:p-3">
                <span className={`text-xs font-mono px-2 py-0.5 rounded-sm border ${
                  c.riskProfile === 'Bajo' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                  c.riskProfile === 'Moderado' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' :
                  c.riskProfile === 'Alto' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                  'bg-red-500/10 text-red-400 border-red-500/20'
                }`}>{c.riskProfile}</span>
              </td>
              <td className="p-2.5 md:p-3 font-mono text-[#A3A3A3] text-xs">{c.exchange}</td>
              <td className="p-2.5 md:p-3 font-mono text-[#A3A3A3] text-xs">{c.marketCap}</td>
              <td className="p-2.5 md:p-3 text-[#A3A3A3] text-xs">{c.objective}</td>
              <td className="p-2.5 md:p-3 text-[#737373] text-xs font-mono">{c.keyFilters}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ComparativeTable;
