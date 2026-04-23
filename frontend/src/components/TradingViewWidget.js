import { useMemo, memo } from 'react';

const TradingViewWidget = memo(({ symbol = 'NASDAQ:AAPL' }) => {
  const src = useMemo(() => {
    const config = {
      autosize: true,
      symbol: symbol,
      interval: 'D',
      timezone: 'America/New_York',
      theme: 'dark',
      style: '1',
      locale: 'es',
      backgroundColor: 'rgba(5, 5, 5, 1)',
      gridColor: 'rgba(255, 255, 255, 0.04)',
      allow_symbol_change: true,
      calendar: false,
      hide_side_toolbar: false,
      details: true,
      hotlist: true,
      support_host: 'https://www.tradingview.com'
    };
    return `https://www.tradingview-widget.com/embed-widget/advanced-chart/?locale=es#${encodeURIComponent(JSON.stringify(config))}`;
  }, [symbol]);

  return (
    <div style={{ height: '550px', width: '100%' }} data-testid="tradingview-widget">
      <iframe
        src={src}
        style={{ width: '100%', height: '100%', border: 'none', display: 'block' }}
        title="TradingView Advanced Chart"
        sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"
        loading="lazy"
      />
    </div>
  );
});

TradingViewWidget.displayName = 'TradingViewWidget';
export default TradingViewWidget;
