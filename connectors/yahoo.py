"""
Connector para Yahoo Finance via librería yfinance.
No hace scraping directo a finance.yahoo.com.
Instalar: pip install yfinance
"""
import logging
import time

import yfinance as yf

from connectors.cache import cached

logger = logging.getLogger("morgana.yahoo")


def _yf_call(label: str, fn):
    """Ejecuta fn() con 3 intentos y backoff exponencial (1s, 2s)."""
    last_exc = None
    for attempt in range(3):
        if attempt > 0:
            wait = 2 ** (attempt - 1)  # 1s, 2s
            logger.warning("Retry %d/2 para %s — esperando %ds", attempt, label, wait)
            time.sleep(wait)
        try:
            result = fn()
            logger.info("OK yfinance %s", label)
            return result
        except Exception as exc:
            last_exc = exc
    raise last_exc


def get_ticker(ticker: str) -> yf.Ticker:
    """Devuelve el objeto Ticker de yfinance."""
    return yf.Ticker(ticker.upper())


@cached(ttl=3600)
def get_info(ticker: str) -> dict:
    """
    Devuelve información general y ratios del ticker.
    Incluye: sector, industry, marketCap, trailingPE, forwardPE,
    priceToBook, debtToEquity, currentRatio, returnOnEquity,
    revenueGrowth, operatingMargins, freeCashflow, etc.
    """
    t = get_ticker(ticker)
    return _yf_call(f"{ticker}/info", lambda: t.info)


def get_price(ticker: str) -> float:
    """Devuelve el precio actual (currentPrice o regularMarketPrice)."""
    info = get_info(ticker)
    return info.get("currentPrice") or info.get("regularMarketPrice")


def get_financials(ticker: str) -> dict:
    """
    Devuelve estados financieros anuales:
    - income_stmt: Estado de resultados
    - balance_sheet: Balance general
    - cashflow: Flujo de caja
    """
    t = get_ticker(ticker)
    return {
        "income_stmt": _yf_call(f"{ticker}/income_stmt", lambda: t.income_stmt),
        "balance_sheet": _yf_call(f"{ticker}/balance_sheet", lambda: t.balance_sheet),
        "cashflow": _yf_call(f"{ticker}/cashflow", lambda: t.cashflow),
    }


def get_quarterly_financials(ticker: str) -> dict:
    """Devuelve estados financieros trimestrales."""
    t = get_ticker(ticker)
    return {
        "income_stmt": _yf_call(f"{ticker}/quarterly_income_stmt", lambda: t.quarterly_income_stmt),
        "balance_sheet": _yf_call(f"{ticker}/quarterly_balance_sheet", lambda: t.quarterly_balance_sheet),
        "cashflow": _yf_call(f"{ticker}/quarterly_cashflow", lambda: t.quarterly_cashflow),
    }


def get_history(ticker: str, period: str = "1y", interval: str = "1d"):
    """
    Devuelve datos OHLCV históricos.
    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """
    t = get_ticker(ticker)
    return _yf_call(f"{ticker}/history({period},{interval})", lambda: t.history(period=period, interval=interval))


def get_recommendations(ticker: str) -> object:
    """Devuelve recomendaciones de analistas."""
    t = get_ticker(ticker)
    return _yf_call(f"{ticker}/recommendations", lambda: t.recommendations)


def get_earnings_dates(ticker: str) -> object:
    """Devuelve fechas de earnings próximas e históricas."""
    t = get_ticker(ticker)
    return _yf_call(f"{ticker}/earnings_dates", lambda: t.earnings_dates)


def get_institutional_holders(ticker: str) -> object:
    """Devuelve los principales holders institucionales."""
    t = get_ticker(ticker)
    return _yf_call(f"{ticker}/institutional_holders", lambda: t.institutional_holders)


def get_insider_transactions(ticker: str) -> object:
    """Devuelve transacciones recientes de insiders."""
    t = get_ticker(ticker)
    return _yf_call(f"{ticker}/insider_transactions", lambda: t.insider_transactions)


def get_options_chain(ticker: str, expiration: str = None) -> dict:
    """
    Devuelve cadena de opciones.
    Si no se especifica expiration, usa la más próxima disponible.
    """
    t = get_ticker(ticker)
    expirations = _yf_call(f"{ticker}/options", lambda: t.options)
    if not expirations:
        return {}
    exp = expiration if expiration in expirations else expirations[0]
    chain = _yf_call(f"{ticker}/option_chain({exp})", lambda: t.option_chain(exp))
    return {"expiration": exp, "calls": chain.calls, "puts": chain.puts}


def get_key_ratios(ticker: str) -> dict:
    """
    Extrae los ratios clave para el análisis de los 4 pilares de Morgana.
    Fuente: yfinance info dict.
    """
    info = get_info(ticker)
    return {
        # Pilar 1 - Moat
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "marketCap": info.get("marketCap"),
        # Pilar 2 - Salud financiera
        "debtToEquity": info.get("debtToEquity"),
        "currentRatio": info.get("currentRatio"),
        "quickRatio": info.get("quickRatio"),
        "freeCashflow": info.get("freeCashflow"),
        "operatingMargins": info.get("operatingMargins"),
        "grossMargins": info.get("grossMargins"),
        "ebitdaMargins": info.get("ebitdaMargins"),
        # Pilar 3 - Crecimiento
        "revenueGrowth": info.get("revenueGrowth"),
        "earningsGrowth": info.get("earningsGrowth"),
        "returnOnEquity": info.get("returnOnEquity"),
        "returnOnAssets": info.get("returnOnAssets"),
        # Valoración
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "priceToBook": info.get("priceToBook"),
        "enterpriseToEbitda": info.get("enterpriseToEbitda"),
        "enterpriseToRevenue": info.get("enterpriseToRevenue"),
        # Pilar 4 - Management
        "heldPercentInsiders": info.get("heldPercentInsiders"),
        "heldPercentInstitutions": info.get("heldPercentInstitutions"),
        # Dividendo
        "dividendYield": info.get("dividendYield"),
        "payoutRatio": info.get("payoutRatio"),
        "dividendRate": info.get("dividendRate"),
        # Precio
        "currentPrice": info.get("currentPrice"),
        "52WeekHigh": info.get("fiftyTwoWeekHigh"),
        "52WeekLow": info.get("fiftyTwoWeekLow"),
        "targetMeanPrice": info.get("targetMeanPrice"),
    }
