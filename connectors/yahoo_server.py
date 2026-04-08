"""
MCP Server para Yahoo Finance (yfinance).
Expone las funciones del connector yahoo.py como herramientas MCP.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from connectors import yahoo

mcp = FastMCP("yahoo")


@mcp.tool()
def yahoo_get_info(ticker: str) -> dict:
    """
    Devuelve información general y ratios del ticker.
    Incluye: sector, industry, marketCap, trailingPE, forwardPE,
    priceToBook, debtToEquity, revenueGrowth, freeCashflow, etc.
    """
    return yahoo.get_info(ticker)


@mcp.tool()
def yahoo_get_price(ticker: str) -> float:
    """Devuelve el precio actual del ticker (currentPrice o regularMarketPrice)."""
    return yahoo.get_price(ticker)


@mcp.tool()
def yahoo_get_key_ratios(ticker: str) -> dict:
    """
    Extrae los ratios clave para el análisis de los 5 pilares de Morgana:
    moat, finanzas growth, motor de crecimiento, management, contexto.
    """
    return yahoo.get_key_ratios(ticker)


@mcp.tool()
def yahoo_get_financials(ticker: str) -> dict:
    """
    Devuelve estados financieros anuales:
    income_stmt, balance_sheet, cashflow (como strings serializados).
    """
    result = yahoo.get_financials(ticker)
    # Convertir DataFrames a string para serialización MCP
    return {k: str(v) for k, v in result.items()}


@mcp.tool()
def yahoo_get_quarterly_financials(ticker: str) -> dict:
    """Devuelve estados financieros trimestrales (income, balance, cashflow)."""
    result = yahoo.get_quarterly_financials(ticker)
    return {k: str(v) for k, v in result.items()}


@mcp.tool()
def yahoo_get_history(ticker: str, period: str = "1y", interval: str = "1d") -> str:
    """
    Devuelve datos OHLCV históricos como string.
    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """
    return str(yahoo.get_history(ticker, period, interval))


@mcp.tool()
def yahoo_get_recommendations(ticker: str) -> str:
    """Devuelve recomendaciones de analistas para el ticker."""
    return str(yahoo.get_recommendations(ticker))


@mcp.tool()
def yahoo_get_earnings_dates(ticker: str) -> str:
    """Devuelve fechas de earnings próximas e históricas."""
    return str(yahoo.get_earnings_dates(ticker))


@mcp.tool()
def yahoo_get_institutional_holders(ticker: str) -> str:
    """Devuelve los principales holders institucionales."""
    return str(yahoo.get_institutional_holders(ticker))


@mcp.tool()
def yahoo_get_insider_transactions(ticker: str) -> str:
    """Devuelve transacciones recientes de insiders (compras/ventas)."""
    return str(yahoo.get_insider_transactions(ticker))


if __name__ == "__main__":
    mcp.run()
