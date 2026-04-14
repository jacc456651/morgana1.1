import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { cacerias } from "@/data/cacerias";
import { originalTips, advancedTips } from "@/data/tips";
import TradingViewWidget from "@/components/TradingViewWidget";
import CaceriaCard from "@/components/CaceriaCard";
import ComparativeTable from "@/components/ComparativeTable";
import {
  Menu, X, Star, ChevronRight, TrendingUp, Target, Zap, Building2,
  BarChart3, Search, Calendar, Map, AlertCircle, ArrowRight,
  Copy, Check, ExternalLink, BookOpen, Settings, Layers, LineChart,
  Shield, Flame, Eye, Crosshair, Repeat, LayoutGrid
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const heroImg = "https://static.prod-images.emergentagent.com/jobs/12bdab86-0a95-4423-8e32-e6c714c3f096/images/9c5a14a71aee5cdf6d696d4f3d383c91ec404268739383eaae8b2e64333672c2.png";

const navItems = [
  { id: "hero", label: "Inicio", icon: Flame },
  { id: "intro", label: "Que es Finviz", icon: BookOpen },
  { id: "setup", label: "Setup inicial", icon: Settings },
  { id: "pestanas", label: "Las 4 pestanas", icon: Layers },
  { id: "resultados", label: "Leer resultados", icon: Eye },
  { id: "tradingview", label: "TradingView", icon: LineChart },
  { id: "comparativa", label: "Tabla Comparativa", icon: LayoutGrid },
  { divider: true },
  ...cacerias.map((c) => ({ id: c.id, label: `${c.label} ${c.name}`, icon: Crosshair, color: c.color })),
  { divider: true },
  { id: "protips", label: "Pro Tips", icon: Zap },
  { id: "errores", label: "Errores comunes", icon: AlertCircle },
  { id: "workflow", label: "Workflow", icon: ArrowRight },
];

const tipIcons = { repeat: Repeat, calendar: Calendar, map: Map, 'bar-chart': BarChart3, target: Target, zap: Zap, search: Search, building: Building2 };

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [copiedUrl, setCopiedUrl] = useState(null);
  const [tvSymbol, setTvSymbol] = useState("NASDAQ:AAPL");

  const fetchFavorites = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/favorites`);
      setFavorites(res.data);
    } catch (e) {
      console.error("Error fetching favorites:", e);
    }
  }, []);

  useEffect(() => { fetchFavorites(); }, [fetchFavorites]);

  const toggleFavorite = async (caceria) => {
    const isFav = favorites.some((f) => f.caceria_id === caceria.id);
    try {
      if (isFav) {
        await axios.delete(`${API}/favorites/${caceria.id}`);
      } else {
        await axios.post(`${API}/favorites`, { caceria_id: caceria.id, caceria_name: caceria.name });
      }
      fetchFavorites();
    } catch (e) {
      console.error("Error toggling favorite:", e);
    }
  };

  const copyUrl = (url, id) => {
    navigator.clipboard.writeText(url);
    setCopiedUrl(id);
    setTimeout(() => setCopiedUrl(null), 2000);
  };

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-[#FAFAFA]">
      {/* Mobile top bar */}
      <header className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-black/70 backdrop-blur-xl border-b border-white/[0.08] px-4 py-3 flex items-center justify-between" data-testid="mobile-header">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1" data-testid="mobile-menu-btn">
          {sidebarOpen ? <X size={22} className="text-[#FAFAFA]" /> : <Menu size={22} className="text-[#FAFAFA]" />}
        </button>
        <span className="font-heading text-lg gold-text font-semibold tracking-tight">MORGANA</span>
        <div className="w-8" />
      </header>

      {/* Sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/60 drawer-backdrop z-30 lg:hidden" onClick={() => setSidebarOpen(false)} data-testid="sidebar-overlay" />
      )}

      {/* Sidebar */}
      <aside className={`fixed top-0 left-0 h-full w-60 bg-[#0A0A0A] border-r border-white/[0.08] z-40 transform transition-transform duration-300 ease-out lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} overflow-y-auto`} data-testid="sidebar">
        <div className="p-5 border-b border-white/[0.06]">
          <h2 className="font-heading text-xl gold-text font-semibold">MORGANA</h2>
          <p className="text-[11px] text-[#737373] mt-0.5 font-mono tracking-wider">GUIA FINVIZ SCREENER</p>
        </div>
        <nav className="py-2 px-2">
          {navItems.map((item, i) =>
            item.divider ? (
              <div key={`d-${i}`} className="h-px bg-white/[0.06] my-2 mx-2" />
            ) : (
              <button
                key={item.id}
                onClick={() => scrollTo(item.id)}
                className="flex items-center gap-2.5 w-full text-left px-3 py-1.5 text-[13px] text-[#A3A3A3] hover:text-[#FAFAFA] hover:bg-white/[0.04] rounded-sm transition-colors group"
                data-testid={`nav-${item.id}`}
              >
                {item.icon && <item.icon size={14} className="shrink-0 text-[#737373] group-hover:text-[#C5A059] transition-colors" style={item.color ? { color: item.color } : {}} />}
                <span className="truncate">{item.label}</span>
              </button>
            )
          )}
        </nav>
      </aside>

      {/* Main content */}
      <main className="lg:ml-60 pt-14 lg:pt-0">
        {/* HERO */}
        <section id="hero" className="relative min-h-[85vh] lg:min-h-screen flex items-center overflow-hidden" data-testid="hero-section">
          <img src={heroImg} alt="" className="absolute inset-0 w-full h-full object-cover opacity-40" />
          <div className="hero-overlay absolute inset-0" />
          <div className="relative z-10 max-w-4xl mx-auto px-5 md:px-10 py-20">
            <div className="font-mono text-[11px] md:text-xs uppercase tracking-[0.3em] text-[#C5A059] mb-6">Sistema MORGANA &middot; Operaciones</div>
            <h1 className="font-heading text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight leading-[1.1] mb-6">
              Guia Finviz<br /><span className="gold-text">para el Analista Senior</span>
            </h1>
            <p className="text-base md:text-lg text-[#A3A3A3] leading-relaxed max-w-2xl mb-10">
              Finviz es el screener mas poderoso disponible de forma gratuita. Esta guia te convierte
              en un operador experto: desde configurar los exchanges hasta ejecutar las 8 Cacerias
              del sistema MORGANA con filtros exactos y criterios de seleccion institucionales.
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 stagger-children">
              {[
                { icon: BarChart3, text: "8 Cacerias documentadas" },
                { icon: Target, text: "Filtros exactos por seccion" },
                { icon: Zap, text: "URLs directas con un clic" },
                { icon: Building2, text: "Estilo institucional" },
              ].map((m, i) => (
                <div key={i} className="flex items-center gap-2.5 p-3 border border-white/[0.08] bg-white/[0.03] animate-fade-in-up">
                  <m.icon size={16} className="text-[#C5A059] shrink-0" />
                  <span className="text-xs md:text-sm text-[#A3A3A3]">{m.text}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* SECTION 1: INTRO */}
        <section id="intro" className="px-5 md:px-10 py-16 md:py-24 max-w-5xl mx-auto" data-testid="section-intro">
          <SectionHeader num="1" title="Que es Finviz y por que usarlo?" />
          <p className="text-sm md:text-base text-[#A3A3A3] leading-relaxed mb-6">
            Finviz (Financial Visualizations) es un screener de acciones que cubre mas de <strong className="text-[#FAFAFA]">8,000 tickers</strong> de
            NYSE, NASDAQ y AMEX. Permite filtrar simultaneamente por mas de 70 criterios: fundamentales,
            tecnicos, descriptivos y de propiedad.
          </p>
          <Callout type="tip" title="El rol de Finviz en MORGANA">
            Finviz es el paso 0: reduce el universo de 8,000 empresas a 20-100 candidatas en segundos.
            Luego EDGAR, Yahoo Finance y StockAnalysis validan los datos con rigor institucional.
            Nunca tomes una decision final basada solo en Finviz.
          </Callout>
          <h3 className="font-heading text-lg md:text-xl text-[#FAFAFA] mt-8 mb-4">Dos modos de uso</h3>
          <DataTable
            headers={["Modo", "URL", "Para que"]}
            rows={[
              ["Screener", "finviz.com/screener.ashx", "Filtrar el universo completo por criterios multiples"],
              ["Quote", "finviz.com/quote.ashx?t=TICKER", "Snapshot completo de una empresa especifica"],
            ]}
          />
        </section>

        {/* SECTION 2: SETUP */}
        <section id="setup" className="px-5 md:px-10 py-16 md:py-24 max-w-5xl mx-auto border-t border-white/[0.06]" data-testid="section-setup">
          <SectionHeader num="2" title="Setup inicial: lo que siempre configuras primero" />
          <p className="text-sm md:text-base text-[#A3A3A3] leading-relaxed mb-6">
            Antes de agregar cualquier filtro financiero, configura estos parametros base que aplican
            a <em>todas</em> las cacerias. Estan en la pestana <TabPill type="descriptive">Descriptive</TabPill>.
          </p>
          <h3 className="font-heading text-lg md:text-xl text-[#FAFAFA] mt-8 mb-4">Exchange: NYSE o NASDAQ?</h3>
          <DataTable
            headers={["Exchange", "Que contiene", "Para las Cacerias"]}
            rows={[
              ["NYSE", "Blue chips, industriales, financieros, utilities, REITs", "C2 (Value), C4 (Dividendos), C8 (Pairs)"],
              ["NASDAQ", "Tecnologia, biotech, growth, SaaS, small caps", "C1 (Growth), C5 (Hidden Gems), C6 (Mega-Trend)"],
              ["AMEX", "Micro caps, warrants, ETFs, empresas muy pequenas", "Excluir siempre - demasiado ruido"],
              ["Sin filtro", "Todo el universo", "C3 (Turnaround), C7 (Shorts)"],
            ]}
          />
          <Callout type="warning" title="AMEX = ruido" className="mt-6">
            AMEX incluye empresas con liquidez minima, spreads amplios y muchas en proceso de delisting. Excluyelo siempre.
          </Callout>
          <h3 className="font-heading text-lg md:text-xl text-[#FAFAFA] mt-8 mb-4">Filtros base universales</h3>
          <div className="grid gap-2">
            {[
              { filter: "Average Volume", value: "Over 100K", why: "Liquidez minima. Sin volumen no puedes entrar ni salir." },
              { filter: "Price", value: "Over $5", why: "Elimina penny stocks con spreads insanos y manipulacion." },
              { filter: "Country", value: "USA", why: "ADRs tienen riesgo de divisa y reporting diferente." },
              { filter: "Market Cap", value: "Segun caceria", why: "El default de MORGANA: Small+ ($300M+)." },
            ].map((f, i) => (
              <div key={i} className="flex flex-col md:flex-row md:items-center gap-1 md:gap-4 p-3 bg-white/[0.02] border-l-2 border-[#C5A059]/40">
                <span className="text-xs font-mono text-[#C5A059] shrink-0 w-32">{f.filter}</span>
                <span className="text-sm font-mono text-[#FAFAFA] shrink-0 w-28">{f.value}</span>
                <span className="text-xs text-[#737373] flex-1">{f.why}</span>
              </div>
            ))}
          </div>
        </section>

        {/* SECTION 3: TABS */}
        <section id="pestanas" className="px-5 md:px-10 py-16 md:py-24 max-w-5xl mx-auto border-t border-white/[0.06]" data-testid="section-pestanas">
          <SectionHeader num="3" title="Las 4 pestanas del screener" />
          <p className="text-sm md:text-base text-[#A3A3A3] leading-relaxed mb-6">
            El screener organiza sus 70+ filtros en 4 pestanas. Entender que hay en cada una es critico.
          </p>
          <DataTable
            headers={["Pestana", "Que contiene", "Filtros clave MORGANA"]}
            rows={[
              [<TabPill type="descriptive">Descriptive</TabPill>, "Exchange, sector, industria, pais, market cap, precio, volumen", "Exchange, Market Cap, Country, Volume, Price"],
              [<TabPill type="fundamental">Fundamental</TabPill>, "P/E, PEG, P/S, P/B, P/FCF, margenes, ROE, deuda, crecimiento", "Gross Margin, ROE, D/E, EPS Growth, Sales Growth"],
              [<TabPill type="technical">Technical</TabPill>, "RSI, SMA, performance vs 52W, beta, volatilidad, patrones", "RSI, 52W High/Low, Performance, Beta"],
              [<TabPill type="all">All</TabPill>, "Todos los filtros en una sola pagina", "Usar cuando combines filtros de multiples pestanas"],
            ]}
          />
          <Callout type="tip" title='Pro tip: usa siempre la pestana "All"' className="mt-6">
            Cuando construyas un screener con filtros de Descriptive + Fundamental + Technical,
            ve directo a la pestana All. Ves todo en una sola pagina y puedes ajustar sin saltar entre pestanas.
          </Callout>
          <h3 className="font-heading text-lg md:text-xl text-[#FAFAFA] mt-8 mb-4">Mapa de filtros fundamentales mas usados</h3>
          <div className="table-scroll">
            <DataTable
              headers={["Filtro", "Que mide", "Senal alcista", "Senal bajista"]}
              rows={[
                ["P/E", "Precio / Ganancias trailing", "<15 value, <30 growth", ">100 sin crecimiento"],
                ["Forward P/E", "Precio / Ganancias estimadas", "Mucho menor que P/E trailing", "Mayor que trailing"],
                ["PEG", "P/E / tasa de crecimiento", "<1 subvalorado", ">2 caro"],
                ["EPS growth this Y", "Crecimiento EPS ano actual", ">20% aceleracion", "Negativo = contraccion"],
                ["Sales growth QoQ", "Revenue trimestral vs ano anterior", ">10% momentum fuerte", "Negativo = deterioro"],
                ["Gross Margin", "Margen bruto %", ">50% SaaS, >30% otros", "<15% commodity"],
                ["ROE", "Return on Equity", ">15% sostenido = moat", "<10% en sector competitivo"],
                ["Debt/Equity", "Deuda total / Patrimonio", "<0.5 growth, <1 value", ">2 riesgo insolvencia"],
                ["Insider Own", "% float en manos insiders", ">10% skin in the game", "<1% management desconectado"],
                ["Short Float", "% float vendido en corto", ">20% contrarian/squeeze", "Confirma tesis bajista"],
                ["P/FCF", "Precio / Free Cash Flow", "<15 generadora de caja", ">50 sin crecimiento"],
              ]}
            />
          </div>
        </section>

        {/* SECTION 4: RESULTS */}
        <section id="resultados" className="px-5 md:px-10 py-16 md:py-24 max-w-5xl mx-auto border-t border-white/[0.06]" data-testid="section-resultados">
          <SectionHeader num="4" title="Como leer los resultados del screener" />
          <p className="text-sm md:text-base text-[#A3A3A3] leading-relaxed mb-6">
            Finviz muestra resultados en tabla, 20 empresas por pagina, ordenables por cualquier columna.
            Checklist mental del analista senior:
          </p>
          <ol className="space-y-3">
            {[
              { bold: "Ticker y nombre:", text: "Lo conoces? Si no, abre el quote en nueva pestana." },
              { bold: "Market Cap:", text: "Esta en el rango que buscas? Un $50B en hidden gems es ruido." },
              { bold: "P/E y Forward P/E:", text: "El Forward es menor? Senal de mejora esperada." },
              { bold: "EPS growth this Y vs past 5Y:", text: "Esta acelerando o desacelerando?" },
              { bold: "Analyst Recom:", text: "De 1 (Strong Buy) a 5 (Sell). <=2 es alcista institucional." },
              { bold: "52W High/Low:", text: "Cerca del minimo? Turnaround. Cerca del maximo? Momentum." },
              { bold: "Volume vs Average:", text: "Si el volumen es 3x el promedio, algo esta pasando." },
            ].map((item, i) => (
              <li key={i} className="flex gap-3 items-start">
                <span className="w-6 h-6 flex items-center justify-center shrink-0 font-mono text-xs text-[#C5A059] border border-[#C5A059]/30 bg-[#C5A059]/5">{i + 1}</span>
                <p className="text-sm text-[#A3A3A3]"><strong className="text-[#FAFAFA]">{item.bold}</strong> {item.text}</p>
              </li>
            ))}
          </ol>
        </section>

        {/* DIVIDER */}
        <div className="border-t border-[#C5A059]/20 mx-5 md:mx-10" />

        {/* TRADINGVIEW */}
        <section id="tradingview" className="px-5 md:px-10 py-16 md:py-24 max-w-6xl mx-auto" data-testid="section-tradingview">
          <SectionHeader num={<LineChart size={18} />} title="TradingView Advanced Chart" />
          <p className="text-sm md:text-base text-[#A3A3A3] leading-relaxed mb-6">
            Analiza el comportamiento tecnico de cualquier ticker directamente aqui. Cambia el simbolo para explorar las candidatas de tus cacerias.
          </p>
          <div className="flex flex-wrap gap-2 mb-6">
            {["NASDAQ:AAPL", "NASDAQ:MSFT", "NASDAQ:NVDA", "NYSE:V", "NASDAQ:GOOGL", "NASDAQ:TSLA"].map((s) => (
              <button
                key={s}
                onClick={() => setTvSymbol(s)}
                className={`text-xs font-mono px-3 py-1.5 border transition-colors ${tvSymbol === s ? "bg-[#C5A059] text-black border-[#C5A059]" : "border-white/10 text-[#A3A3A3] hover:border-white/20 hover:text-[#FAFAFA]"}`}
                data-testid={`tv-symbol-${s.replace(":", "-")}`}
              >
                {s.split(":")[1]}
              </button>
            ))}
          </div>
          <div className="border border-white/[0.08] bg-[#0A0A0A]">
            <TradingViewWidget symbol={tvSymbol} />
          </div>
        </section>

        {/* COMPARATIVE TABLE */}
        <section id="comparativa" className="px-5 md:px-10 py-16 md:py-24 max-w-6xl mx-auto border-t border-white/[0.06]" data-testid="section-comparativa">
          <SectionHeader num={<LayoutGrid size={18} />} title="Tabla Comparativa de Cacerias" />
          <p className="text-sm md:text-base text-[#A3A3A3] leading-relaxed mb-6">
            Comparacion lado a lado de las 8 estrategias del sistema MORGANA. Usa esta tabla como referencia rapida.
          </p>
          <div className="border border-white/[0.08] bg-[#0A0A0A]">
            <ComparativeTable cacerias={cacerias} />
          </div>
        </section>

        {/* DIVIDER */}
        <div className="border-t border-[#C5A059]/20 mx-5 md:mx-10" />

        {/* CACERIAS C1-C8 */}
        <div className="px-5 md:px-10 py-16 md:py-24 max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <div className="font-mono text-[11px] uppercase tracking-[0.3em] text-[#C5A059] mb-3">Las 8 Estrategias</div>
            <h2 className="font-heading text-2xl sm:text-3xl lg:text-4xl font-semibold tracking-tight">Las Cacerias de MORGANA</h2>
          </div>
          <div className="space-y-6 stagger-children">
            {cacerias.map((c) => (
              <div key={c.id} id={c.id} className="animate-fade-in-up">
                <CaceriaCard
                  caceria={c}
                  isFavorite={favorites.some((f) => f.caceria_id === c.id)}
                  onToggleFavorite={() => toggleFavorite(c)}
                  onCopyUrl={copyUrl}
                  copied={copiedUrl === c.id}
                />
              </div>
            ))}
          </div>
        </div>

        {/* DIVIDER */}
        <div className="border-t border-[#C5A059]/20 mx-5 md:mx-10" />

        {/* PRO TIPS */}
        <section id="protips" className="px-5 md:px-10 py-16 md:py-24 max-w-6xl mx-auto" data-testid="section-protips">
          <SectionHeader num={<Star size={18} />} title="Tips de analista senior" />

          <h3 className="font-heading text-lg md:text-xl text-[#FAFAFA] mt-8 mb-5">Tips Fundamentales</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-12">
            {originalTips.map((tip) => {
              const Icon = tipIcons[tip.icon] || Zap;
              return (
                <div key={tip.id} className="p-4 border border-white/[0.08] bg-[#111111] hover:border-white/[0.15] transition-all hover:-translate-y-0.5" data-testid={`tip-${tip.id}`}>
                  <div className="flex items-center gap-2.5 mb-2">
                    <Icon size={15} className="text-[#C5A059] shrink-0" />
                    <h4 className="text-sm font-semibold text-[#FAFAFA]">{tip.title}</h4>
                  </div>
                  <p className="text-xs md:text-sm text-[#A3A3A3] leading-relaxed">{tip.text}</p>
                </div>
              );
            })}
          </div>

          <h3 className="font-heading text-lg md:text-xl text-[#FAFAFA] mb-5">
            Estrategias Avanzadas <span className="text-[#C5A059]">MORGANA</span>
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 stagger-children">
            {advancedTips.map((tip) => (
              <div key={tip.id} className="p-4 border border-white/[0.08] bg-[#111111] hover:border-[#C5A059]/30 transition-all hover:-translate-y-0.5 animate-fade-in-up group" data-testid={`tip-${tip.id}`}>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-[#FAFAFA] leading-snug">{tip.title}</h4>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 bg-[#C5A059]/10 text-[#C5A059] border border-[#C5A059]/20 shrink-0 ml-2">{tip.badge}</span>
                </div>
                <p className="text-xs text-[#A3A3A3] leading-relaxed font-mono whitespace-pre-line mb-2">{tip.text}</p>
                <p className="text-xs text-[#C5A059] leading-relaxed">{tip.insight}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ERRORES COMUNES */}
        <section id="errores" className="px-5 md:px-10 py-16 md:py-24 max-w-5xl mx-auto border-t border-white/[0.06]" data-testid="section-errores">
          <SectionHeader num="!" title="Errores que comete el analista novato" />
          <div className="space-y-3 mt-6">
            {[
              { title: "Demasiados filtros = 0 resultados", text: "Empieza con 3 filtros core, ve sumando. Si tienes 0, quita el menos importante." },
              { title: "Confundir EPS growth con Sales growth", text: "Una empresa puede tener EPS creciendo 50% (por recompras) con revenue estancado. Revenue growth es la metrica primaria." },
              { title: "Ignorar el market cap range", text: "Un screener de growth con empresas de $500B y $300M mezcladas es inutil. Define el rango." },
              { title: "No verificar en fuente primaria", text: "Finviz tiene hasta 24h de delay. Para decisiones serias, valida con EDGAR (10-K, 10-Q)." },
              { title: "Comprar porque salio en el screener", text: "El screener da candidatas, NO senales de compra. Despues viene: leer 10-K, analizar earnings call, validar moat." },
              { title: "Ignorar Short Float alto", text: "Short Float >30% = muchos profesionales apuestan en contra. Debes saber POR QUE estan short." },
              { title: "Usar Finviz en vez de EDGAR para tesis final", text: "Finviz muestra ROE de 25%. EDGAR puede mostrar que fue por una ganancia one-time." },
            ].map((err, i) => (
              <div key={i} className="flex gap-3 items-start p-4 border border-white/[0.06] bg-red-500/[0.03] hover:bg-red-500/[0.05] transition-colors" data-testid={`error-${i}`}>
                <div className="w-5 h-5 flex items-center justify-center shrink-0 bg-red-500/20 rounded-full">
                  <AlertCircle size={12} className="text-red-400" />
                </div>
                <div>
                  <strong className="text-sm text-[#FAFAFA] block mb-0.5">{err.title}</strong>
                  <p className="text-xs md:text-sm text-[#A3A3A3] leading-relaxed">{err.text}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* WORKFLOW */}
        <section id="workflow" className="px-5 md:px-10 py-16 md:py-24 max-w-5xl mx-auto border-t border-white/[0.06]" data-testid="section-workflow">
          <SectionHeader num={<ArrowRight size={18} />} title="Workflow MORGANA: Finviz a Analisis profundo" />
          <p className="text-sm md:text-base text-[#A3A3A3] leading-relaxed mb-8">
            Finviz es el primer eslabon de un proceso de 6 pasos:
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-10">
            {[
              { icon: Search, label: "Finviz Screener", sub: "8,000 -> 20-50" },
              { icon: BarChart3, label: "Yahoo / StockAnalysis", sub: "Datos detallados" },
              { icon: BookOpen, label: "EDGAR 10-K / 10-Q", sub: "Validar en fuente" },
              { icon: Shield, label: "/analiza TICKER", sub: "Reporte MORGANA" },
              { icon: Target, label: "/consejo TICKER", sub: "Tesis + antitesis" },
              { icon: Check, label: "/asignacion", sub: "Decision final" },
            ].map((step, i) => (
              <div key={i} className="flex flex-col items-center text-center p-4 border border-white/[0.08] bg-[#111111] hover:border-[#C5A059]/30 transition-colors group">
                <step.icon size={20} className="text-[#C5A059] mb-2 group-hover:scale-110 transition-transform" />
                <span className="text-xs font-semibold text-[#FAFAFA] mb-0.5">{step.label}</span>
                <span className="text-[10px] text-[#737373]">{step.sub}</span>
                {i < 5 && <ChevronRight size={12} className="text-[#737373] mt-2 hidden lg:block" />}
              </div>
            ))}
          </div>

          <h3 className="font-heading text-lg md:text-xl text-[#FAFAFA] mt-10 mb-4">Las 3 preguntas que todo screener debe responder</h3>
          <DataTable
            headers={["#", "Pregunta", "Donde verificar"]}
            rows={[
              ["1", "El negocio es bueno? (moat, margenes, ROIC)", "Finviz -> EDGAR 10-K -> /analiza"],
              ["2", "El management es bueno? (insider own, track record)", "Finviz -> Yahoo insider -> Earnings calls"],
              ["3", "El precio es razonable? (PEG, P/FCF, EV/Sales)", "Finviz -> /comps -> /dcf"],
            ]}
          />
        </section>

        {/* FOOTER */}
        <footer className="px-5 md:px-10 py-8 border-t border-white/[0.06] max-w-5xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-3">
            <span className="text-xs text-[#737373]">Sistema MORGANA &middot; Guia Finviz Screener &middot; Actualizado 2026</span>
            <span className="text-xs text-[#737373]">Inspirado en: Fisher &middot; Lynch &middot; Akre &middot; Smith</span>
          </div>
        </footer>
      </main>
    </div>
  );
}

/* Reusable sub-components */

function SectionHeader({ num, title }) {
  return (
    <div className="flex items-center gap-4 mb-6">
      <div className="section-num">{num}</div>
      <h2 className="font-heading text-xl sm:text-2xl lg:text-3xl font-semibold tracking-tight">{title}</h2>
    </div>
  );
}

function Callout({ type = "tip", title, children, className = "" }) {
  const styles = {
    tip: "border-[#C5A059] bg-[#C5A059]/5",
    warning: "border-amber-500 bg-amber-500/5",
    danger: "border-red-500 bg-red-500/5",
    success: "border-emerald-500 bg-emerald-500/5",
  };
  const icons = {
    tip: <Zap size={14} className="text-[#C5A059]" />,
    warning: <AlertCircle size={14} className="text-amber-500" />,
    danger: <AlertCircle size={14} className="text-red-500" />,
    success: <Check size={14} className="text-emerald-500" />,
  };
  return (
    <div className={`border-l-2 pl-4 py-3 ${styles[type]} ${className}`}>
      <div className="flex items-center gap-2 mb-1">
        {icons[type]}
        <strong className="text-sm text-[#FAFAFA]">{title}</strong>
      </div>
      <p className="text-xs md:text-sm text-[#A3A3A3] leading-relaxed">{children}</p>
    </div>
  );
}

function TabPill({ type, children }) {
  const cls = `tab-${type}`;
  return <span className={`${cls} text-[10px] md:text-xs px-2 py-0.5 rounded-sm font-mono inline-block`}>{children}</span>;
}

function DataTable({ headers, rows }) {
  return (
    <div className="table-scroll">
      <table className="w-full text-sm min-w-[500px]">
        <thead>
          <tr className="border-b border-white/10">
            {headers.map((h, i) => (
              <th key={i} className="text-left p-2.5 font-mono text-[10px] md:text-xs text-[#C5A059] uppercase tracking-[0.1em]">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
              {row.map((cell, j) => (
                <td key={j} className="p-2.5 text-xs md:text-sm text-[#A3A3A3]">
                  {j === 0 ? <span className="font-mono text-[#FAFAFA] font-medium">{cell}</span> : cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
