"""
MCP Server para StockAnalysis.com.
Expone las funciones del connector stockanalysis_client.py como herramientas MCP.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from connectors import stockanalysis_client as sa

mcp = FastMCP("stockanalysis")


@mcp.tool()
def stockanalysis_get_income_statement(ticker: str) -> list:
    """
    Extrae el estado de resultados anual de StockAnalysis.com.
    Devuelve lista de dicts con métricas: Revenue, Gross Profit, Net Income, EPS, etc.
    """
    return sa.get_income_statement(ticker)


@mcp.tool()
def stockanalysis_get_balance_sheet(ticker: str) -> list:
    """
    Extrae el balance general anual de StockAnalysis.com.
    Devuelve lista de dicts con métricas: Total Assets, Total Debt, Cash, Equity, etc.
    """
    return sa.get_balance_sheet(ticker)


@mcp.tool()
def stockanalysis_get_cash_flow(ticker: str) -> list:
    """
    Extrae el estado de flujo de caja anual de StockAnalysis.com.
    Devuelve lista de dicts: Operating CF, CapEx, Free Cash Flow, etc.
    """
    return sa.get_cash_flow(ticker)


@mcp.tool()
def stockanalysis_get_ratios(ticker: str) -> list:
    """
    Extrae ratios financieros anuales de StockAnalysis.com.
    Devuelve lista de dicts: P/E, P/S, P/FCF, ROE, ROIC, Gross Margin, etc.
    """
    return sa.get_ratios(ticker)


@mcp.tool()
def stockanalysis_get_all_financials(ticker: str) -> dict:
    """
    Extrae todos los datos financieros disponibles para un ticker:
    income_statement, balance_sheet, cash_flow, ratios.
    """
    return sa.get_all_financials(ticker)


if __name__ == "__main__":
    mcp.run()
