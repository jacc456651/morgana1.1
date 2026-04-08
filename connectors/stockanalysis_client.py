"""
Connector para StockAnalysis.com
Extrae datos financieros usando requests + BeautifulSoup.
Instalar: pip install requests beautifulsoup4

URLs:
- Income statement : https://stockanalysis.com/stocks/{ticker}/financials/
- Balance sheet    : https://stockanalysis.com/stocks/{ticker}/financials/balance-sheet/
- Cash flow        : https://stockanalysis.com/stocks/{ticker}/financials/cash-flow-statement/
- Ratios           : https://stockanalysis.com/stocks/{ticker}/financials/ratios/
"""

import logging
import time

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("morgana.stockanalysis")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

BASE_URL = "https://stockanalysis.com/stocks/{ticker}/financials{path}"


def _fetch_page(url: str) -> BeautifulSoup:
    """Descarga la pagina y retorna objeto BeautifulSoup."""
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
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as exc:
            last_exc = exc

    raise last_exc


def _extract_table(soup: BeautifulSoup) -> list:
    """
    Extrae la tabla financiera principal de la pagina.
    Retorna lista de dicts: [{"metric": "Revenue", "2024": "391B", ...}, ...]
    """
    table = soup.find("table")
    if not table:
        return []

    headers = []
    rows = []

    thead = table.find("thead")
    if thead:
        for th in thead.find_all("th"):
            headers.append(th.get_text(strip=True))

    tbody = table.find("tbody")
    if tbody:
        for tr in tbody.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if len(cells) > 1:
                row = {"metric": cells[0]}
                for i, val in enumerate(cells[1:], 1):
                    if i < len(headers):
                        row[headers[i]] = val
                rows.append(row)

    return rows


def get_income_statement(ticker: str) -> list:
    """Extrae el estado de resultados anual."""
    url = BASE_URL.format(ticker=ticker.lower(), path="/")
    soup = _fetch_page(url)
    return _extract_table(soup)


def get_balance_sheet(ticker: str) -> list:
    """Extrae el balance general anual."""
    url = BASE_URL.format(ticker=ticker.lower(), path="/balance-sheet/")
    soup = _fetch_page(url)
    return _extract_table(soup)


def get_cash_flow(ticker: str) -> list:
    """Extrae el estado de flujo de caja anual."""
    url = BASE_URL.format(ticker=ticker.lower(), path="/cash-flow-statement/")
    soup = _fetch_page(url)
    return _extract_table(soup)


def get_ratios(ticker: str) -> list:
    """Extrae los ratios financieros anuales."""
    url = BASE_URL.format(ticker=ticker.lower(), path="/ratios/")
    soup = _fetch_page(url)
    return _extract_table(soup)


def get_all_financials(ticker: str) -> dict:
    """
    Extrae todos los datos financieros disponibles para un ticker.
    Retorna dict con: income_statement, balance_sheet, cash_flow, ratios.
    """
    ticker = ticker.upper()
    print(f"Extrayendo datos de StockAnalysis para {ticker}...")

    endpoints = {
        "income_statement": get_income_statement,
        "balance_sheet": get_balance_sheet,
        "cash_flow": get_cash_flow,
        "ratios": get_ratios,
    }

    result = {}
    for name, func in endpoints.items():
        try:
            data = func(ticker)
            result[name] = data
            print(f"  OK {name}: {len(data)} metricas extraidas")
        except Exception as e:
            result[name] = []
            print(f"  ERROR {name}: {e}")

    return result


if __name__ == "__main__":
    import json

    data = get_all_financials("AAPL")

    print("\n=== RESULTADOS AAPL ===")
    for section, rows in data.items():
        print(f"\n--- {section.upper()} ({len(rows)} filas) ---")
        for row in rows[:8]:
            print(f"  {row}")
        if len(rows) > 8:
            print(f"  ... y {len(rows) - 8} metricas mas")
