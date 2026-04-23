export const originalTips = [
  {
    id: 'ot1',
    icon: 'repeat',
    title: 'Itera con menos filtros primero',
    text: 'Empieza con 3 filtros fuertes. Si tienes 200+ resultados, agrega uno mas. Si tienes 0, quita el mas restrictivo. El sweet spot es 15-50 resultados.'
  },
  {
    id: 'ot2',
    icon: 'calendar',
    title: 'Corre el screener los lunes',
    text: 'Los mercados procesan noticias el fin de semana. El lunes a las 9:30 AM hay mispricing temporal. Los screeners de lunes capturan gap downs injustificados que el mercado corrige durante la semana.'
  },
  {
    id: 'ot3',
    icon: 'map',
    title: 'Usa el Heatmap antes del screener',
    text: 'El mapa de calor de Finviz te da el contexto macro en 5 segundos. Si energia esta todo rojo y tecnologia todo verde, ajusta tus cacerias al contexto del dia.'
  },
  {
    id: 'ot4',
    icon: 'bar-chart',
    title: 'EPS growth QoQ vs past 5Y',
    text: 'Si EPS crecio 30% los ultimos 5 anos pero este ano solo 5%, la empresa esta desacelerando. Si crecio 10% historicamente pero este ano 25%, esta acelerando. La aceleracion vale mas que el numero absoluto.'
  },
  {
    id: 'ot5',
    icon: 'target',
    title: 'Analyst Recom como senal contrarian',
    text: 'En C5 (Hidden Gems), busca empresas con Analyst Recom vacio o muy pocos analistas. Las mejores oportunidades estan donde Wall Street no llega aun.'
  },
  {
    id: 'ot6',
    icon: 'zap',
    title: 'El combo asesino: EPS+Sales+PEG',
    text: 'EPS growth this Y >20% + Sales growth >10% + PEG <2 + ROE >15% + D/E <0.5 es el screener de calidad-crecimiento mas potente que existe. Rara vez da mas de 10 resultados.'
  },
  {
    id: 'ot7',
    icon: 'search',
    title: 'Short Float como senal de dos caras',
    text: 'Short Float >20% puede significar: (a) el mercado sabe algo que tu no - INVESTIGA antes de comprar. (b) oportunidad de squeeze si los fundamentals son buenos.'
  },
  {
    id: 'ot8',
    icon: 'building',
    title: 'Sector peers como benchmark',
    text: 'Despues del screener, usa la pestana de Sector/Industry en el quote individual para ver la empresa vs sus peers. Una empresa con P/E de 20 puede ser barata si sus peers cotizan a 40.'
  }
];

export const advancedTips = [
  {
    id: 'at1',
    title: '1. Pullback en Uptrend (el santo grial de momentum)',
    text: 'Technical: Price above SMA200 + SMA50\n+ Performance (Month) -15% to 0%\n+ RSI(14) 45-65\n+ Sales growth QoQ > 10%',
    insight: 'Encuentras empresas fuertes en correccion sana.',
    badge: 'Momentum'
  },
  {
    id: 'at2',
    title: '2. Short Squeeze Candidates 2.0',
    text: 'Short Float > 20% + Relative Volume > 3 + Insider Transactions Positive + Price near 52W Low',
    insight: 'Este combo es extremadamente asimetrico cuando coincide con earnings cercanos.',
    badge: 'Squeeze'
  },
  {
    id: 'at3',
    title: '3. Relative Strength vs Sector',
    text: 'Usa la pestana "All" y agrega:\nPerformance (Week) > Sector Performance\nPerformance (Month) > Sector Performance',
    insight: 'Filtra las mejores empresas dentro de un sector fuerte.',
    badge: 'Strength'
  },
  {
    id: 'at4',
    title: '4. Institutional Accumulation',
    text: 'Institutional Ownership > 70% + Net Insider Buying (Positive) + Float < 50M',
    insight: 'Muestra que los grandes jugadores estan acumulando discretamente.',
    badge: 'Institucional'
  },
  {
    id: 'at5',
    title: '5. Earnings Momentum Filter',
    text: 'EPS growth this Y > 25% + EPS growth next 5Y > 20% + Surprise % (last quarter) > 15%',
    insight: 'Las empresas que mas superan expectativas tienden a seguir subiendo.',
    badge: 'Earnings'
  },
  {
    id: 'at6',
    title: '6. Low Float + High Short Interest (micro explosiva)',
    text: 'Market Cap Micro + Float < 20M + Short Float > 25% + Relative Volume > 5',
    insight: 'Usalo solo en C5 Hidden Gems y con stop-loss muy ajustado.',
    badge: 'Micro Cap'
  },
  {
    id: 'at7',
    title: '7. Pre-Market / Gap Strategy',
    text: 'Corre el screener los lunes a las 8:30 AM (hora NY) con:\nGap Up/Down + Relative Volume > 4',
    insight: 'Los mejores setups del dia aparecen en las primeras 2 horas.',
    badge: 'Pre-Market'
  },
  {
    id: 'at8',
    title: '8. Sector Rotation Automatico',
    text: 'Abre finviz.com/map.ashx -> mira que sector esta mas verde -> filtra solo ese sector + Sales growth QoQ > 15%',
    insight: 'Rotacion sectorial es una de las estrategias mas rentables del 2025-2026.',
    badge: 'Rotacion'
  },
  {
    id: 'at9',
    title: '9. URL Hack (compartir screeners avanzados)',
    text: 'Despues de armar tu screener, copia la URL completa y pegala en un Notion o Google Doc.',
    insight: 'Puedes agregar &o=-salesqoq al final para ordenar automaticamente.',
    badge: 'Hack'
  },
  {
    id: 'at10',
    title: '10. Elite + Free Combo (2026)',
    text: 'Usa Finviz Free para descubrir -> Finviz Elite solo para alertas en tiempo real y export CSV ilimitado.',
    insight: 'El ROI del Elite se paga solo con una buena operacion al mes.',
    badge: 'Pro Combo'
  },
  {
    id: 'at11',
    title: '11. Contrarian Signal',
    text: 'Analyst Recom = 4 o 5 (Sell/Hold fuerte) + Insider Transactions Very Positive + Short Float > 15%',
    insight: 'Cuando los analistas odian y los insiders compran = senal contrarian muy potente.',
    badge: 'Contrarian'
  },
  {
    id: 'at12',
    title: '12. Master Filter (el mas restrictivo de MORGANA)',
    text: 'Sales growth past 5Y > 20% + ROE > 20% + Debt/Equity < 0.3 + PEG < 1.2 + Insider Own > 10%',
    insight: 'Este filtro casi siempre devuelve menos de 8-15 empresas de altisima calidad.',
    badge: 'Master'
  }
];
