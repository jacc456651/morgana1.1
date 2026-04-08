"""
MCP Server para Finviz.
Expone las funciones del connector finviz.py como herramientas MCP.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from connectors import finviz

mcp = FastMCP("finviz")


@mcp.tool()
def finviz_get_snapshot(ticker: str) -> dict:
    """
    Obtiene el snapshot completo de ratios de Finviz para un ticker.
    Incluye P/E, EPS, ROE, ROI, sector, industria, volumen, etc.
    """
    return finviz.get_snapshot(ticker)


@mcp.tool()
def finviz_get_key_metrics(ticker: str) -> dict:
    """
    Extrae métricas clave de Finviz relevantes para el análisis Morgana:
    PEG, P/FCF, EPS growth, ROE, ROI, márgenes, insider ownership,
    analyst recommendation, target price, RSI, beta.
    """
    return finviz.get_key_metrics(ticker)


@mcp.tool()
def finviz_get_sector_peers(ticker: str) -> list:
    """
    Devuelve lista de hasta 20 peers del mismo sector/industria según Finviz,
    ordenados por market cap descendente.
    """
    return finviz.get_sector_peers(ticker)


if __name__ == "__main__":
    mcp.run()
