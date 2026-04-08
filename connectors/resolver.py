"""
Resolver de datos financieros con fallback entre fuentes.
Orden de prioridad: Yahoo Finance → Finviz → StockAnalysis
"""
import logging

from connectors import yahoo, finviz, stockanalysis_client as stockanalysis

logger = logging.getLogger("morgana.resolver")


def get_financials(ticker: str) -> dict:
    """
    Obtiene ratios financieros intentando las fuentes en orden.
    Retorna {"data": {...}, "source": "yahoo|finviz|stockanalysis"}.
    Si todas fallan, retorna {"data": {}, "source": None}.
    """
    sources = [
        ("yahoo",         lambda: yahoo.get_key_ratios(ticker)),
        ("finviz",        lambda: finviz.get_key_metrics(ticker)),
        ("stockanalysis", lambda: stockanalysis.get_ratios(ticker)),
    ]

    for name, fetch in sources:
        try:
            data = fetch()
            logger.info("Fuente '%s' exitosa para %s", name, ticker)
            return {"data": data, "source": name}
        except Exception as exc:
            logger.warning("Fuente '%s' falló para %s: %s", name, ticker, exc)

    logger.error("Todas las fuentes fallaron para %s", ticker)
    return {"data": {}, "source": None}
