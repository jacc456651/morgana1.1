"""
Connector para FRED (Federal Reserve Economic Data).
Requiere FRED_API_KEY en .env — gratis en fred.stlouisfed.org/docs/api/api_key.html
"""
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("morgana.fred")

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "fed_funds_rate": "DFF",
    "treasury_10y": "GS10",
    "cpi": "CPIAUCSL",
    "unemployment": "UNRATE",
    "gdp": "GDP",
}


def _get_api_key() -> str:
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise ValueError("FRED_API_KEY requerida en .env (gratis en fred.stlouisfed.org)")
    return key


def _get(series_id: str) -> dict:
    resp = requests.get(
        FRED_BASE_URL,
        params={
            "series_id": series_id,
            "api_key": _get_api_key(),
            "file_type": "json",
            "sort_order": "desc",
            "limit": 1,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_series_latest(series_id: str) -> float | None:
    """Retorna el valor más reciente de una serie FRED. None si no disponible o error."""
    try:
        data = _get(series_id)
        observations = data.get("observations", [])
        if observations:
            val = observations[0].get("value", ".")
            return float(val) if val != "." else None
    except Exception as exc:
        logger.warning("[FRED] Error en serie %s: %s", series_id, exc)
    return None


def get_macro_context() -> dict:
    """
    Retorna las 5 series macro más relevantes para el pilar P5 (Contexto/Timing).
    Nunca lanza excepción — retorna None por cada serie que falle.
    P5 usa: fed_funds_rate (costo de capital), treasury_10y (tasa libre de riesgo para DCF),
    cpi (inflación erosiona márgenes), unemployment (ciclo económico), gdp (salud macro).
    """
    return {
        name: get_series_latest(series_id)
        for name, series_id in SERIES.items()
    }
