"""
Connector para EDGAR (SEC).
Todas las requests incluyen User-Agent requerido por la SEC.
Fuentes: data.sec.gov, efts.sec.gov
"""
import logging
import os
import time

import requests

from connectors.cache import cached

logger = logging.getLogger("morgana.edgar")

# Requerido por la SEC: https://www.sec.gov/os/accessing-edgar-data
HEADERS = {
    "User-Agent": os.environ.get("SEC_USER_AGENT", "financial-analysis-bot@example.com"),
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}

BASE_URL = "https://data.sec.gov"
EFTS_URL = "https://efts.sec.gov"


def _get(url: str, params: dict = None) -> dict:
    """GET con headers SEC obligatorios. Lanza excepción si falla."""
    # Ajustar Host según dominio
    headers = HEADERS.copy()
    if "efts.sec.gov" in url:
        headers["Host"] = "efts.sec.gov"

    last_exc = None
    for attempt in range(3):
        if attempt > 0:
            wait = 2 ** (attempt - 1)  # 1s, 2s
            logger.warning("Retry %d/2 para %s — esperando %ds", attempt, url, wait)
            time.sleep(wait)
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            logger.info("GET %s → %d", url, resp.status_code)
            return resp.json()
        except requests.RequestException as exc:
            last_exc = exc

    raise last_exc


_cik_cache: dict = {}


def get_cik(ticker: str) -> str:
    """
    Devuelve el CIK de 10 dígitos para un ticker dado.
    Usa el índice companytickers.json de la SEC.
    """
    ticker_up = ticker.upper()
    if ticker_up in _cik_cache:
        return _cik_cache[ticker_up]

    headers = HEADERS.copy()
    headers["Host"] = "www.sec.gov"
    resp = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    companies = resp.json()

    for entry in companies.values():
        if entry.get("ticker", "").upper() == ticker_up:
            cik = str(entry["cik_str"]).zfill(10)
            _cik_cache[ticker_up] = cik
            return cik

    raise ValueError(f"Ticker '{ticker_up}' no encontrado en EDGAR companytickers.json")


@cached(ttl=3600)
def get_company_facts(ticker: str) -> dict:
    """Devuelve todos los hechos XBRL de la empresa (10-K, 10-Q, etc.)."""
    cik = get_cik(ticker)
    return _get(f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json")


@cached(ttl=3600)
def get_submissions(ticker: str) -> dict:
    """Devuelve el historial de filings de la empresa."""
    cik = get_cik(ticker)
    return _get(f"{BASE_URL}/submissions/CIK{cik}.json")


def get_latest_10k(ticker: str) -> dict:
    """Devuelve metadata del 10-K más reciente."""
    subs = get_submissions(ticker)
    filings = subs.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    dates = filings.get("filingDate", [])
    accessions = filings.get("accessionNumber", [])
    urls = filings.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form == "10-K":
            cik = subs.get("cik", "").zfill(10)
            acc = accessions[i].replace("-", "")
            doc = urls[i]
            return {
                "form": form,
                "date": dates[i],
                "accessionNumber": accessions[i],
                "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}",
                "edgarUrl": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=include&count=10",
            }
    return {}


def get_latest_10q(ticker: str) -> dict:
    """Devuelve metadata del 10-Q más reciente."""
    subs = get_submissions(ticker)
    filings = subs.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    dates = filings.get("filingDate", [])
    accessions = filings.get("accessionNumber", [])
    urls = filings.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form == "10-Q":
            cik = subs.get("cik", "").zfill(10)
            acc = accessions[i].replace("-", "")
            doc = urls[i]
            return {
                "form": form,
                "date": dates[i],
                "accessionNumber": accessions[i],
                "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}",
            }
    return {}


def search_filings(ticker: str, form_type: str = "10-K", hits: int = 5) -> list:
    """Busca filings en EFTS (full-text search index)."""
    headers = HEADERS.copy()
    headers["Host"] = "efts.sec.gov"
    params = {
        "q": f'"{ticker}"',
        "dateRange": "custom",
        "forms": form_type,
        "_source": "file_date,period_of_report,entity_name,file_num",
        "hits.hits._source": "file_date",
        "hits.hits.total": hits,
    }
    resp = requests.get(
        f"{EFTS_URL}/LATEST/search-index?q=%22{ticker}%22&forms={form_type}",
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("hits", {}).get("hits", [])


def get_metric(ticker: str, concept: str, unit: str = "USD") -> list:
    """
    Extrae una métrica XBRL específica de companyfacts.
    Ejemplo: get_metric('AAPL', 'us-gaap/Revenues')
    Devuelve lista de {'end': date, 'val': value, 'form': form}.
    """
    facts = get_company_facts(ticker)
    try:
        namespace, tag = concept.split("/")
        entries = facts["facts"][namespace][tag]["units"][unit]
        # Filtrar solo filings anuales (form 10-K) y ordenar por fecha
        annual = [e for e in entries if e.get("form") == "10-K"]
        annual.sort(key=lambda x: x["end"])
        return annual
    except (KeyError, ValueError):
        return []
