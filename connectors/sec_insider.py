"""
Connector para Form 4 (insider transactions) de SEC EDGAR.
Usa el endpoint submissions de data.sec.gov — ya cubierto por SEC_USER_AGENT en .env.
Cuenta transacciones de insiders (Form 4) en los últimos 12 meses para P4 Management.
"""
import logging
import os
from datetime import datetime, timedelta

import requests

from connectors import edgar

logger = logging.getLogger("morgana.sec_insider")

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
HEADERS = {
    "User-Agent": os.environ.get("SEC_USER_AGENT", "financial-analysis-bot@example.com"),
    "Accept-Encoding": "gzip, deflate",
}


def _get_submissions(cik: str) -> dict:
    """Descarga el JSON de submissions para un CIK dado."""
    cik_padded = cik.lstrip("0").zfill(10)
    url = SUBMISSIONS_URL.format(cik=cik_padded)
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _parse_form4_filings(submissions: dict, months: int = 12) -> dict:
    """
    Filtra Form 4 dentro de los últimos `months` meses.
    Retorna count y fechas recientes sin parsear XML.
    """
    cutoff = datetime.now() - timedelta(days=months * 30)
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])

    form4_dates = [
        dates[i]
        for i, form in enumerate(forms)
        if form == "4" and i < len(dates)
        and datetime.fromisoformat(dates[i]) >= cutoff
    ]

    return {
        "count_12m": len(form4_dates),
        "recent_dates": form4_dates[:5],
    }


def get_insider_transactions(ticker: str) -> dict:
    """
    Retorna el conteo de Form 4 (insider transactions) de los últimos 12 meses.
    P4 signal: >5 filings en 12m con insider buying = señal positiva de conviction.
    Nunca lanza excepción — retorna dict con count=0 si falla.
    """
    try:
        cik = edgar.get_cik(ticker)
        submissions = _get_submissions(cik)
        return _parse_form4_filings(submissions)
    except Exception as exc:
        logger.warning("[Insiders] Error para %s: %s", ticker, exc)
        return {"count_12m": 0, "recent_dates": []}
