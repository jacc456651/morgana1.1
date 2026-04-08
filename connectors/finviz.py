"""
Connector para Finviz.
Fuente: finviz.com — screener y comparaciones sectoriales.
Nota: Macrotrends y WSJ han sido eliminados como fuentes.
"""
import logging
import time

import requests
from html.parser import HTMLParser

from connectors.cache import cached

logger = logging.getLogger("morgana.finviz")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

BASE_URL = "https://finviz.com"


class _FinvizTableParser(HTMLParser):
    """Parser minimalista para extraer la tabla de ratios de Finviz."""

    def __init__(self):
        super().__init__()
        self.data = {}
        self._in_table = False
        self._cells = []
        self._current = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "table" and "snapshot-table2" in attrs_dict.get("class", ""):
            self._in_table = True
        if self._in_table and tag == "td":
            self._current = ""

    def handle_endtag(self, tag):
        if tag == "table" and self._in_table:
            self._in_table = False
        if self._in_table and tag == "td" and self._current is not None:
            self._cells.append(self._current.strip())
            self._current = None
            # Cada par (label, value)
            if len(self._cells) >= 2 and len(self._cells) % 2 == 0:
                label = self._cells[-2]
                value = self._cells[-1]
                if label:
                    self.data[label] = value

    def handle_data(self, data):
        if self._current is not None:
            self._current += data


@cached(ttl=3600)
def get_snapshot(ticker: str) -> dict:
    """
    Obtiene el snapshot de ratios de Finviz para un ticker.
    Devuelve dict con métricas como P/E, EPS, ROE, ROI, etc.
    """
    url = f"{BASE_URL}/quote.ashx?t={ticker.upper()}"

    last_exc = None
    for attempt in range(3):
        if attempt > 0:
            wait = 2 ** (attempt - 1)  # 1s, 2s
            logger.warning("Retry %d/2 para %s — esperando %ds", attempt, url, wait)
            time.sleep(wait)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            logger.info("GET %s → %d", url, resp.status_code)

            parser = _FinvizTableParser()
            parser.feed(resp.text)

            # Si el parser no capturó nada, intentar extracción alternativa
            if not parser.data:
                return _parse_snapshot_fallback(resp.text)

            return parser.data
        except requests.RequestException as exc:
            last_exc = exc

    raise last_exc


def _parse_snapshot_fallback(html: str) -> dict:
    """
    Extracción alternativa buscando patrones data-boxover en el HTML.
    Devuelve dict vacío si no encuentra datos.
    """
    import re
    data = {}
    # Buscar pares label/value en celdas de la tabla snapshot
    matches = re.findall(
        r'<td[^>]*class="[^"]*snapshot-td2-cp[^"]*"[^>]*>(.*?)</td>.*?'
        r'<td[^>]*class="[^"]*snapshot-td2[^"]*"[^>]*>(.*?)</td>',
        html,
        re.DOTALL,
    )
    for label, value in matches:
        # Limpiar HTML tags
        label_clean = re.sub(r"<[^>]+>", "", label).strip()
        value_clean = re.sub(r"<[^>]+>", "", value).strip()
        if label_clean:
            data[label_clean] = value_clean
    return data


def get_sector_peers(ticker: str) -> list:
    """
    Devuelve lista de peers del mismo sector según Finviz.
    Usa el screener filtrado por sector de la empresa.
    """
    # Primero obtenemos el sector del ticker
    snapshot = get_snapshot(ticker)
    sector = snapshot.get("Sector", "")
    industry = snapshot.get("Industry", "")

    if not sector:
        return []

    # Screener por sector e industria
    params = {
        "v": "111",
        "f": f"sec_{sector.lower().replace(' ', '_')},ind_{industry.lower().replace(' ', '_')}",
        "o": "-marketcap",
    }
    url = f"{BASE_URL}/screener.ashx"

    last_exc = None
    resp = None
    for attempt in range(3):
        if attempt > 0:
            wait = 2 ** (attempt - 1)  # 1s, 2s
            logger.warning("Retry %d/2 para %s — esperando %ds", attempt, url, wait)
            time.sleep(wait)
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            resp.raise_for_status()
            logger.info("GET %s → %d", url, resp.status_code)
            break
        except requests.RequestException as exc:
            last_exc = exc
            resp = None

    if resp is None:
        raise last_exc

    import re
    # Extraer tickers de los resultados del screener
    tickers = re.findall(r'quote\.ashx\?t=([A-Z]+)"', resp.text)
    # Eliminar duplicados manteniendo orden
    seen = set()
    unique = []
    for t in tickers:
        if t not in seen and t != ticker.upper():
            seen.add(t)
            unique.append(t)
    return unique[:20]


def get_key_metrics(ticker: str) -> dict:
    """
    Extrae métricas clave del snapshot de Finviz relevantes para Morgana.
    """
    raw = get_snapshot(ticker)
    return {
        "P/E": raw.get("P/E"),
        "Forward P/E": raw.get("Forward P/E"),
        "PEG": raw.get("PEG"),
        "P/S": raw.get("P/S"),
        "P/B": raw.get("P/B"),
        "P/C": raw.get("P/C"),
        "P/FCF": raw.get("P/FCF"),
        "EPS (ttm)": raw.get("EPS (ttm)"),
        "EPS growth this Y": raw.get("EPS growth this Y"),
        "EPS growth next Y": raw.get("EPS growth next Y"),
        "EPS growth next 5Y": raw.get("EPS growth next 5Y"),
        "Sales growth past 5Y": raw.get("Sales growth past 5Y"),
        "ROE": raw.get("ROE"),
        "ROI": raw.get("ROI"),
        "ROA": raw.get("ROA"),
        "Debt/Eq": raw.get("Debt/Eq"),
        "Current Ratio": raw.get("Current Ratio"),
        "Gross Margin": raw.get("Gross Margin"),
        "Oper. Margin": raw.get("Oper. Margin"),
        "Profit Margin": raw.get("Profit Margin"),
        "Short Float": raw.get("Short Float"),
        "Insider Own": raw.get("Insider Own"),
        "Inst Own": raw.get("Inst Own"),
        "Avg Volume": raw.get("Avg Volume"),
        "Market Cap": raw.get("Market Cap"),
        "Sector": raw.get("Sector"),
        "Industry": raw.get("Industry"),
        "Country": raw.get("Country"),
        "Analyst Recom": raw.get("Recom"),
        "Target Price": raw.get("Target Price"),
        "52W High": raw.get("52W High"),
        "52W Low": raw.get("52W Low"),
        "RSI (14)": raw.get("RSI (14)"),
        "Beta": raw.get("Beta"),
    }
