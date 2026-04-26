"""
Extractor de short interest a partir del yahoo_info ya recolectado por Scout.
Sin llamadas HTTP — función pura para P5 (Contexto/Timing).
Short interest alto (>20% float) = señal de riesgo o catalizador si hay squeeze.
"""
import logging

logger = logging.getLogger("morgana.short_interest")

_FIELD_MAP = {
    "short_percent_of_float": "shortPercentOfFloat",
    "shares_short": "sharesShort",
    "short_ratio": "shortRatio",
    "shares_short_prior_month": "sharesShortPriorMonth",
    "float_shares": "floatShares",
}


def extract_short_interest(yahoo_info: dict) -> dict:
    """
    Extrae métricas de short interest del dict de Yahoo Finance.
    Calcula cambio MoM en shares short si ambos valores están disponibles.
    """
    result = {key: yahoo_info.get(yf_key) for key, yf_key in _FIELD_MAP.items()}

    current = result.get("shares_short")
    prior = result.get("shares_short_prior_month")
    if current and prior and prior > 0:
        result["shares_short_change_pct"] = round((current - prior) / prior * 100, 2)
    else:
        result["shares_short_change_pct"] = None

    return result
