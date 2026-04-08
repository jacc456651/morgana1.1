"""
MCP Server para EDGAR (SEC).
Expone las funciones del connector edgar.py como herramientas MCP.
"""
import sys
import os

# Asegurar que el directorio raíz del proyecto esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from connectors import edgar

mcp = FastMCP("edgar")


@mcp.tool()
def edgar_get_cik(ticker: str) -> str:
    """Devuelve el CIK de 10 dígitos de la SEC para un ticker dado."""
    return edgar.get_cik(ticker)


@mcp.tool()
def edgar_get_latest_10k(ticker: str) -> dict:
    """Devuelve metadata del 10-K más reciente (fecha, URL, número de acceso)."""
    return edgar.get_latest_10k(ticker)


@mcp.tool()
def edgar_get_latest_10q(ticker: str) -> dict:
    """Devuelve metadata del 10-Q más reciente (fecha, URL, número de acceso)."""
    return edgar.get_latest_10q(ticker)


@mcp.tool()
def edgar_get_submissions(ticker: str) -> dict:
    """Devuelve el historial completo de filings de la empresa en EDGAR."""
    return edgar.get_submissions(ticker)


@mcp.tool()
def edgar_get_company_facts(ticker: str) -> dict:
    """Devuelve todos los hechos XBRL de la empresa (datos de 10-K, 10-Q, etc.)."""
    return edgar.get_company_facts(ticker)


@mcp.tool()
def edgar_get_metric(ticker: str, concept: str, unit: str = "USD") -> list:
    """
    Extrae una métrica XBRL específica de companyfacts.
    Ejemplos de concept: 'us-gaap/Revenues', 'us-gaap/NetIncomeLoss',
    'us-gaap/Assets', 'us-gaap/StockholdersEquity'.
    Devuelve lista de {'end': date, 'val': value, 'form': form} ordenada por fecha.
    """
    return edgar.get_metric(ticker, concept, unit)


@mcp.tool()
def edgar_search_filings(ticker: str, form_type: str = "10-K", hits: int = 5) -> list:
    """
    Busca filings en el índice full-text de EDGAR (EFTS).
    form_type: '10-K', '10-Q', '8-K', etc.
    """
    return edgar.search_filings(ticker, form_type, hits)


if __name__ == "__main__":
    mcp.run()
