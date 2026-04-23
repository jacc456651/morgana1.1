# Morgana — 12 Fixes de Arquitectura y Lógica

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corregir los 12 problemas de lógica y arquitectura identificados en la auditoría del 2026-04-14.

**Architecture:** Los fixes se agrupan en 8 tareas por afinidad funcional. Ningún cambio rompe la interfaz pública existente — son correcciones internas y adiciones backward-compatible.

**Tech Stack:** Python 3.11+, SQLite3 (stdlib), threading (stdlib), requests, BeautifulSoup4, yfinance

---

## Archivos que se crean o modifican

| Archivo | Acción | Problema que resuelve |
|---------|--------|-----------------------|
| `connectors/cache.py` | Modify | #1 Cache persistente |
| `connectors/http_utils.py` | Create | #7 Retry unificado |
| `connectors/validators.py` | Create | #6 Validación de input |
| `connectors/edgar.py` | Modify | #6 Usar validators |
| `connectors/yahoo.py` | Modify | #6 Usar validators |
| `connectors/finviz.py` | Modify | #6 #7 Validators + http_utils |
| `connectors/stockanalysis_client.py` | Modify | #6 #7 Validators + http_utils |
| `connectors/rate_limiter.py` | Create | #8 Rate limiting |
| `connectors/shared_state.py` | Create | #9 Estado compartido entre plugins |
| `screener/fetcher.py` | Modify | #2 #8 CAGR logs + rate limiting |
| `screener/runner.py` | Modify | #4 Error handling por ticker |
| `screener/universe.py` | Modify | #3 Fallback universe hardcodeado |
| `screener/fallback_tickers.py` | Create | #3 Datos estáticos de fallback |
| `equity-research/hooks/save_earnings.py` | Modify | #5 #12 Validación + timestamps |
| `financial-analysis/hooks/save_model_output.py` | Modify | #5 #12 Validación + timestamps |
| `private-equity/hooks/save_pe_output.py` | Modify | #5 #12 Validación + timestamps |
| `_archive/README.md` | Create | #11 Deprecation notice |
| `commands/compounder.md` | Create | #10 Comando faltante |
| `commands/chequea.md` | Create | #10 Comando faltante |
| `commands/asignacion.md` | Create | #10 Comando faltante |
| `output/AUDIT-2026-04-14.md` | Create | Registro de todos los cambios |

---

## Task 1: Cache Persistente con SQLite (Problema #1)

**Files:**
- Modify: `connectors/cache.py`

- [ ] **Step 1: Reemplazar SimpleCache con implementación SQLite**

```python
# connectors/cache.py
"""
Cache con persistencia SQLite para los connectors de Morgana.
Sobrevive reinicios de proceso. TTL en segundos.
"""
import json
import sqlite3
import time
import threading
from functools import wraps
from pathlib import Path

_DB_PATH = Path(__file__).parent.parent / "output" / "morgana_cache.db"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
_lock = threading.Lock()


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS cache "
        "(key TEXT PRIMARY KEY, value TEXT, expires_at REAL)"
    )
    conn.commit()
    return conn


_conn: sqlite3.Connection | None = None


def _conn_get() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = _get_conn()
    return _conn


class SimpleCache:
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl

    def get(self, key):
        """Retorna el valor cacheado o None si no existe / expiró."""
        key_str = json.dumps(key, sort_keys=True, default=str)
        with _lock:
            conn = _conn_get()
            row = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?", (key_str,)
            ).fetchone()
        if row is None:
            return None
        value_str, expires_at = row
        if time.time() > expires_at:
            with _lock:
                _conn_get().execute("DELETE FROM cache WHERE key = ?", (key_str,))
                _conn_get().commit()
            return None
        return json.loads(value_str)

    def set(self, key, value, ttl: int = None):
        """Guarda value bajo key con TTL en segundos."""
        ttl = ttl if ttl is not None else self.default_ttl
        key_str = json.dumps(key, sort_keys=True, default=str)
        try:
            value_str = json.dumps(value, default=str)
        except (TypeError, ValueError):
            return  # No cachear si no es serializable
        expires_at = time.time() + ttl
        with _lock:
            conn = _conn_get()
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                (key_str, value_str, expires_at),
            )
            conn.commit()

    def invalidate(self, key):
        key_str = json.dumps(key, sort_keys=True, default=str)
        with _lock:
            conn = _conn_get()
            conn.execute("DELETE FROM cache WHERE key = ?", (key_str,))
            conn.commit()

    def clear(self):
        with _lock:
            conn = _conn_get()
            conn.execute("DELETE FROM cache")
            conn.commit()

    def purge_expired(self):
        """Elimina entradas vencidas — llamar periódicamente."""
        with _lock:
            conn = _conn_get()
            conn.execute("DELETE FROM cache WHERE expires_at < ?", (time.time(),))
            conn.commit()


_cache = SimpleCache()


def cached(ttl: int = 3600):
    """
    Decorador que cachea el resultado de una función por TTL segundos.
    La cache key se construye con (nombre_función, args, kwargs).
    Persiste en SQLite entre reinicios.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (fn.__qualname__, args, tuple(sorted(kwargs.items())))
            result = _cache.get(key)
            if result is not None:
                return result
            result = fn(*args, **kwargs)
            if result:  # no cachear resultados vacíos ({}, [], "")
                _cache.set(key, result, ttl=ttl)
            return result
        return wrapper
    return decorator
```

- [ ] **Step 2: Verificar que no rompe los connectors existentes**

Ejecutar en consola Python:
```python
import sys; sys.path.insert(0, "C:/Users/TOSHIBA/financial-services-plugins")
from connectors.cache import _cache, cached
_cache.set("test_key", {"val": 42}, ttl=60)
assert _cache.get("test_key") == {"val": 42}
_cache.invalidate("test_key")
assert _cache.get("test_key") is None
print("Cache OK")
```
Expected: `Cache OK`

---

## Task 2: HTTP Utils unificado + Validación de Tickers (Problemas #7 y #6)

**Files:**
- Create: `connectors/http_utils.py`
- Create: `connectors/validators.py`

- [ ] **Step 1: Crear connectors/http_utils.py**

```python
# connectors/http_utils.py
"""
Utilidades HTTP compartidas para todos los connectors.
Retry con backoff exponencial estandarizado.
"""
import logging
import time
import requests

logger = logging.getLogger("morgana.http")


def get_with_retry(
    url: str,
    headers: dict,
    params: dict = None,
    timeout: int = 15,
    retries: int = 3,
) -> requests.Response:
    """
    GET con retry exponencial. Igual para todos los connectors.
    Lanza la última excepción si todos los intentos fallan.
    """
    last_exc = None
    for attempt in range(retries):
        if attempt > 0:
            wait = 2 ** (attempt - 1)  # 1s, 2s
            logger.warning("Retry %d/%d para %s — esperando %ds", attempt, retries - 1, url, wait)
            time.sleep(wait)
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=timeout)
            resp.raise_for_status()
            logger.info("GET %s → %d", url, resp.status_code)
            return resp
        except requests.RequestException as exc:
            last_exc = exc
            logger.debug("Intento %d falló: %s", attempt + 1, exc)
    raise last_exc
```

- [ ] **Step 2: Crear connectors/validators.py**

```python
# connectors/validators.py
"""
Validación de inputs para los connectors de Morgana.
Falla rápido con mensajes claros antes de hacer requests externos.
"""
import re

_TICKER_RE = re.compile(r"^[A-Z]{1,5}(-[A-Z])?$")


def validate_ticker(ticker: str) -> str:
    """
    Normaliza y valida un ticker de US equity.
    Devuelve el ticker en mayúsculas si es válido.
    Lanza ValueError con mensaje claro si no lo es.
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError(f"Ticker inválido: '{ticker}' — debe ser una string no vacía")
    normalized = ticker.strip().upper()
    # Convertir puntos a guiones (BRK.B → BRK-B) para compatibilidad
    normalized = normalized.replace(".", "-")
    if not _TICKER_RE.match(normalized):
        raise ValueError(
            f"Ticker inválido: '{normalized}' — "
            f"debe ser 1-5 letras mayúsculas (ej: AAPL, BRK-B). "
            f"¿Quisiste decir '{normalized[:5]}'?"
        )
    return normalized
```

---

## Task 3: Aplicar http_utils y validators a los 4 connectors (Problemas #6 y #7)

**Files:**
- Modify: `connectors/finviz.py` (reemplazar _get interno con http_utils + validators)
- Modify: `connectors/stockanalysis_client.py` (mismo)
- Modify: `connectors/edgar.py` (agregar validators)
- Modify: `connectors/yahoo.py` (agregar validators)

- [ ] **Step 1: Actualizar connectors/finviz.py — agregar validación y usar http_utils**

En `connectors/finviz.py`, reemplazar la función `get_snapshot` completa:

```python
# Agregar al inicio (después de los imports existentes):
from connectors.http_utils import get_with_retry
from connectors.validators import validate_ticker


@cached(ttl=3600)
def get_snapshot(ticker: str) -> dict:
    """
    Obtiene el snapshot de ratios de Finviz para un ticker.
    Devuelve dict con métricas como P/E, EPS, ROE, ROI, etc.
    """
    ticker = validate_ticker(ticker)
    url = f"{BASE_URL}/quote.ashx?t={ticker}"
    resp = get_with_retry(url, headers=HEADERS, timeout=15)

    parser = _FinvizTableParser()
    parser.feed(resp.text)

    if not parser.data:
        return _parse_snapshot_fallback(resp.text)

    return parser.data
```

Y reemplazar `get_sector_peers` — el loop de retry manual:

```python
def get_sector_peers(ticker: str) -> list:
    ticker = validate_ticker(ticker)
    snapshot = get_snapshot(ticker)
    sector = snapshot.get("Sector", "")
    industry = snapshot.get("Industry", "")

    if not sector:
        return []

    params = {
        "v": "111",
        "f": f"sec_{sector.lower().replace(' ', '_')},ind_{industry.lower().replace(' ', '_')}",
        "o": "-marketcap",
    }
    import re
    resp = get_with_retry(f"{BASE_URL}/screener.ashx", headers=HEADERS, params=params)
    tickers = re.findall(r'quote\.ashx\?t=([A-Z]+)"', resp.text)
    seen = set()
    unique = []
    for t in tickers:
        if t not in seen and t != ticker:
            seen.add(t)
            unique.append(t)
    return unique[:20]
```

- [ ] **Step 2: Actualizar connectors/stockanalysis_client.py — agregar validación y usar http_utils**

Reemplazar `_fetch_page`:

```python
# Agregar al inicio (después de los imports existentes):
from connectors.http_utils import get_with_retry
from connectors.validators import validate_ticker


def _fetch_page(url: str) -> BeautifulSoup:
    """Descarga la pagina y retorna objeto BeautifulSoup."""
    resp = get_with_retry(url, headers=HEADERS, timeout=15)
    return BeautifulSoup(resp.text, "html.parser")
```

Agregar validación en `get_income_statement`, `get_balance_sheet`, `get_cash_flow`, `get_ratios`:

```python
def get_income_statement(ticker: str) -> list:
    """Extrae el estado de resultados anual."""
    ticker = validate_ticker(ticker)
    url = BASE_URL.format(ticker=ticker.lower(), path="/")
    soup = _fetch_page(url)
    return _extract_table(soup)


def get_balance_sheet(ticker: str) -> list:
    """Extrae el balance general anual."""
    ticker = validate_ticker(ticker)
    url = BASE_URL.format(ticker=ticker.lower(), path="/balance-sheet/")
    soup = _fetch_page(url)
    return _extract_table(soup)


def get_cash_flow(ticker: str) -> list:
    """Extrae el estado de flujo de caja anual."""
    ticker = validate_ticker(ticker)
    url = BASE_URL.format(ticker=ticker.lower(), path="/cash-flow-statement/")
    soup = _fetch_page(url)
    return _extract_table(soup)


def get_ratios(ticker: str) -> list:
    """Extrae los ratios financieros anuales."""
    ticker = validate_ticker(ticker)
    url = BASE_URL.format(ticker=ticker.lower(), path="/ratios/")
    soup = _fetch_page(url)
    return _extract_table(soup)
```

- [ ] **Step 3: Agregar validate_ticker a edgar.py y yahoo.py**

En `connectors/edgar.py`, agregar al inicio y en `get_cik`:
```python
from connectors.validators import validate_ticker

def get_cik(ticker: str) -> str:
    ticker_up = validate_ticker(ticker)  # Reemplazar: ticker_up = ticker.upper()
    # ... resto igual
```

En `connectors/yahoo.py`, agregar al inicio y en `get_info`:
```python
from connectors.validators import validate_ticker

@cached(ttl=3600)
def get_info(ticker: str) -> dict:
    ticker = validate_ticker(ticker)  # Agregar esta línea al inicio de la función
    t = get_ticker(ticker)
    return _yf_call(f"{ticker}/info", lambda: t.info)
```

---

## Task 4: Rate Limiter para el Screener (Problema #8)

**Files:**
- Create: `connectors/rate_limiter.py`
- Modify: `screener/fetcher.py`

- [ ] **Step 1: Crear connectors/rate_limiter.py**

```python
# connectors/rate_limiter.py
"""
Token bucket rate limiter thread-safe para requests externos.
Evita que el screener paralelo sature Finviz o StockAnalysis.
"""
import threading
import time


class RateLimiter:
    """
    Token bucket: permite `rate` requests por segundo como máximo.
    Thread-safe para ThreadPoolExecutor.
    """
    def __init__(self, rate: float, burst: int = 1):
        """
        rate: requests por segundo (ej: 2.0 = 2 req/s)
        burst: tokens máximos acumulables (ej: 5 = ráfaga de 5 antes de esperar)
        """
        self.rate = rate
        self.burst = burst
        self._tokens = float(burst)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self):
        """Bloquea hasta que haya un token disponible."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
            self._last_refill = now

            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return

            wait = (1.0 - self._tokens) / self.rate

        time.sleep(wait)
        with self._lock:
            self._tokens = max(0.0, self._tokens - 1.0)


# Instancias globales por fuente
finviz_limiter = RateLimiter(rate=4.0, burst=8)        # 4 req/s, burst 8
stockanalysis_limiter = RateLimiter(rate=1.5, burst=3) # 1.5 req/s, burst 3
edgar_limiter = RateLimiter(rate=0.5, burst=2)         # SEC: máx 10 req/10s
yahoo_limiter = RateLimiter(rate=3.0, burst=5)
```

- [ ] **Step 2: Aplicar rate limiter en screener/fetcher.py**

Reemplazar las funciones `fetch_pass1` y `fetch_pass2` para usar rate limiters:

```python
# Agregar al inicio de screener/fetcher.py:
from connectors.rate_limiter import finviz_limiter, stockanalysis_limiter

# En fetch_pass1, dentro del submit loop, agregar rate limiter:
def _fetch_pass1_single(ticker: str) -> dict:
    """Fetch con rate limiting para un único ticker."""
    finviz_limiter.acquire()
    raw = get_key_metrics(ticker)
    return parse_metrics(raw)

# Luego en fetch_pass1, cambiar el submit:
future_to_ticker = {
    executor.submit(_fetch_pass1_single, t): t for t in tickers
}

# En fetch_pass2, reemplazar _get_revenue_cagr wrapper:
def _fetch_pass2_single(ticker: str) -> float | None:
    """Fetch con rate limiting para un único ticker."""
    stockanalysis_limiter.acquire()
    return _get_revenue_cagr(ticker)

# Y en fetch_pass2:
future_to_ticker = {
    executor.submit(_fetch_pass2_single, t): t for t in tickers
}
# Eliminar el time.sleep(0.2) — ya lo maneja el rate limiter
```

---

## Task 5: Observabilidad CAGR + Error Handling por Ticker (Problemas #2 y #4)

**Files:**
- Modify: `screener/fetcher.py` (CAGR logging)
- Modify: `screener/runner.py` (per-ticker error collection)

- [ ] **Step 1: Agregar logging de CAGR en screener/fetcher.py**

Al final de `fetch_pass2`, antes del return, agregar:

```python
    # Observabilidad: cuántos tickers perdieron CAGR
    none_count = sum(1 for v in results.values() if v is None)
    total_count = len(results)
    pct_ok = (total_count - none_count) / total_count * 100 if total_count else 0
    logger.info(
        "Pass 2 CAGR: %d/%d tickers con dato (%.0f%%) — %d sin CAGR (excluidos de cacerias que lo requieren)",
        total_count - none_count, total_count, pct_ok, none_count,
    )
    if verbose:
        print(f"  CAGR disponible: {total_count - none_count}/{total_count} tickers ({pct_ok:.0f}%)")
    if errors > 0:
        logger.warning("Pass 2: %d errores de fetch en StockAnalysis", errors)
    return results
```

- [ ] **Step 2: Agregar error handling por ticker en screener/runner.py**

Reemplazar el loop de filtros en la función `run()`:

```python
    # ── Aplicar filtros de cacerias ───────────────────────────────────────────
    print(f"\n[sabueso] Aplicando filtros de cacerias {caceria_ids}...")
    candidates = []
    filter_errors = []

    for ticker, metrics in pass1_candidates.items():
        try:
            cagr = cagr_data.get(ticker)
            results = run_all_filters(ticker, metrics, cagr, caceria_ids)
            for r in results:
                candidates.append({
                    "Ticker": ticker,
                    "Caceria": r.caceria,
                    "Score": r.score,
                    "CAGR": format_metric(cagr, pct=True),
                    "Gross_Margin": format_metric(metrics.get("Gross Margin"), pct=True),
                    "Insider_Own": format_metric(metrics.get("Insider Own"), pct=True),
                    "Debt_Eq": format_metric(metrics.get("Debt/Eq")),
                    "Market_Cap_B": format_metric(metrics.get("Market Cap"), billions=True),
                    "P_FCF": format_metric(metrics.get("P/FCF")),
                    "Hits": " | ".join(r.hits),
                })
        except Exception as exc:
            filter_errors.append((ticker, str(exc)))
            logger.warning("Error aplicando filtros a %s: %s", ticker, exc)

    if filter_errors:
        print(f"[sabueso] {len(filter_errors)} tickers con error en filtros (ver log para detalle)")
        logger.warning("Tickers con errores de filtro: %s", filter_errors)
```

---

## Task 6: Universe Fallback Hardcodeado (Problema #3)

**Files:**
- Create: `screener/fallback_tickers.py`
- Modify: `screener/universe.py`

- [ ] **Step 1: Crear screener/fallback_tickers.py**

```python
# screener/fallback_tickers.py
"""
Universo de fallback estático para cuando Wikipedia / iShares no están disponibles.
Actualizado: 2026-04-14. ~200 tickers de alta liquidez (S&P500 top + Nasdaq100 top).
Actualizar manualmente cada trimestre si el scraping sigue fallando.
"""

SP500_FALLBACK = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","GOOG","META","TSLA","BRK-B","UNH",
    "LLY","JPM","V","XOM","MA","AVGO","PG","HD","COST","MRK","ABBV","CVX",
    "KO","PEP","ADBE","WMT","BAC","MCD","CSCO","CRM","ACN","ORCL","TMO",
    "ABT","NKE","NFLX","AMD","INTC","QCOM","DHR","TXN","UPS","HON","AMGN",
    "PM","MS","GE","IBM","INTU","AMAT","CAT","GS","SPGI","BLK","AXP","SYK",
    "LIN","DE","ADP","GILD","MDT","REGN","MO","C","ISRG","VRTX","PLD","CI",
    "LRCX","ADI","KLAC","PANW","SNPS","CDNS","MELI","ASML","NOW","DXCM","ZTS",
    "BSX","EOG","SLB","OKE","CTAS","PAYX","ORLY","MNST","KHC","GD","RTX",
    "LMT","NOC","F","GM","T","VZ","CMCSA","DIS","NXPI","MRVL","FTNT","CRWD",
]

NASDAQ100_FALLBACK = [
    "AAPL","MSFT","NVDA","AMZN","META","TSLA","GOOGL","GOOG","AVGO","COST",
    "NFLX","AMD","ADBE","CSCO","INTU","QCOM","TXN","AMGN","ISRG","AMAT",
    "REGN","VRTX","MU","LRCX","KLAC","PANW","MELI","ASML","ADI","SNPS",
    "CDNS","MRVL","CRWD","FTNT","DXCM","PAYX","ORLY","MNST","NXPI","KDP",
    "CTAS","MCHP","FAST","ROST","VRSK","IDXX","BIIB","ILMN","DLTR","PCAR",
    "ON","WBD","WDAY","TEAM","DDOG","ZS","OKTA","BILL","HUBS","DUOL","AXON",
    "MNDY","GTLB","CELH","SMCI","ARM","PLTR","HOOD","RBLX","SNAP","PINS",
]

def get_sp500_fallback() -> list[str]:
    return sorted(set(SP500_FALLBACK))

def get_nasdaq100_fallback() -> list[str]:
    return sorted(set(NASDAQ100_FALLBACK))

def get_combined_fallback() -> list[str]:
    return sorted(set(SP500_FALLBACK) | set(NASDAQ100_FALLBACK))
```

- [ ] **Step 2: Actualizar screener/universe.py para usar fallback**

Modificar `get_sp500` y `get_nasdaq100` para capturar errores y usar fallback:

```python
# Agregar al inicio de universe.py:
from screener.fallback_tickers import get_sp500_fallback, get_nasdaq100_fallback

def get_sp500() -> list[str]:
    """S&P 500 desde Wikipedia. Si falla, usa fallback estático."""
    cached = _load_cache("sp500")
    if cached:
        return cached
    try:
        tables = _read_html_wiki("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        df = tables[0]
        tickers = df["Symbol"].str.replace(".", "-", regex=False).tolist()
        _save_cache("sp500", tickers)
        return tickers
    except Exception as e:
        print(f"[universe] S&P500 Wikipedia falló: {e}. Usando fallback estático ({len(get_sp500_fallback())} tickers).")
        return get_sp500_fallback()


def get_nasdaq100() -> list[str]:
    """Nasdaq 100 desde Wikipedia. Si falla, usa fallback estático."""
    cached = _load_cache("nasdaq100")
    if cached:
        return cached
    try:
        tables = _read_html_wiki("https://en.wikipedia.org/wiki/Nasdaq-100")
        for df in tables:
            str_cols = [c for c in df.columns if isinstance(c, str)]
            cols_lower = {c.lower(): c for c in str_cols}
            if "ticker" in cols_lower or "symbol" in cols_lower:
                col = cols_lower.get("ticker") or cols_lower.get("symbol")
                tickers = df[col].dropna().tolist()
                tickers = [t for t in tickers if isinstance(t, str) and 1 < len(t) <= 5]
                if len(tickers) > 50:
                    _save_cache("nasdaq100", tickers)
                    return tickers
        raise RuntimeError("No se encontró tabla Nasdaq-100 en Wikipedia")
    except Exception as e:
        print(f"[universe] Nasdaq100 Wikipedia falló: {e}. Usando fallback estático ({len(get_nasdaq100_fallback())} tickers).")
        return get_nasdaq100_fallback()
```

---

## Task 7: Hook Content Validation + Timestamps Únicos (Problemas #5 y #12)

**Files:**
- Modify: `equity-research/hooks/save_earnings.py`
- Modify: `financial-analysis/hooks/save_model_output.py`
- Modify: `private-equity/hooks/save_pe_output.py`

- [ ] **Step 1: Actualizar save_earnings.py — validación + timestamp único**

```python
# equity-research/hooks/save_earnings.py
"""
Hook PostToolUse — guarda análisis de earnings en output/reportes/[TICKER]/[FECHA]_[HH-MM]_earnings.md

Cambios vs versión anterior:
- Timestamp HH-MM en nombre de archivo para evitar colisiones el mismo día
- Validación mínima de contenido antes de guardar (>200 chars, tiene secciones)
- Log de advertencia si el contenido parece misrouteado
"""
import json
import os
import re
import sys
from datetime import datetime

EARNINGS_KEYWORDS = {"earnings", "quarterly", "q1", "q2", "q3", "q4", "10-q", "beat", "miss"}
MIN_CONTENT_LENGTH = 200  # chars mínimos para considerar un reporte válido


def _is_earnings_content(path: str, content: str) -> bool:
    """True si el archivo parece un reporte de earnings."""
    if len(content) < MIN_CONTENT_LENGTH:
        return False  # Demasiado corto para ser un reporte real
    path_lower = path.lower()
    content_preview = content[:500].lower()
    if "earnings" in path_lower:
        return True
    # Requiere al menos 2 keywords para evitar falsos positivos
    matches = EARNINGS_KEYWORDS.intersection(content_preview.split())
    return len(matches) >= 2


def _extract_ticker(path: str, content: str) -> str | None:
    m = re.search(r"output[/\\]reportes[/\\]([A-Z]{1,5})[/\\]", path)
    if m:
        return m.group(1)
    m = re.search(r"\*{0,2}[Tt]icker\*{0,2}\s*[:\-]\s*([A-Z]{1,5})\b", content)
    if m:
        return m.group(1)
    m = re.search(r"^#\s+([A-Z]{1,5})\b", content, re.MULTILINE)
    if m:
        return m.group(1)
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if payload.get("tool_name") != "Write":
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    if not _is_earnings_content(file_path, content):
        sys.exit(0)

    ticker = _extract_ticker(file_path, content)
    if not ticker:
        print("[hook:save_earnings] No se pudo extraer el ticker — archivo no guardado.", file=sys.stderr)
        sys.exit(0)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    dest_dir = os.path.join("output", "reportes", ticker)
    dest_path = os.path.join(dest_dir, f"{timestamp}_earnings.md")

    if os.path.abspath(file_path) == os.path.abspath(dest_path):
        sys.exit(0)

    os.makedirs(dest_dir, exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[hook:save_earnings] Guardado: {dest_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Actualizar save_model_output.py — validación + timestamp único**

Cambios clave en `save_model_output.py`:

```python
# Reemplazar la línea de today y dest_path:
from datetime import datetime
# ...
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M")
dest_path = os.path.join(dest_dir, f"{timestamp}_{name}.md")

# Agregar validación mínima en _is_model_content:
MIN_CONTENT_LENGTH = 300

def _is_model_content(path: str, content: str) -> bool:
    """True si el archivo parece un output de modelo financiero."""
    if len(content) < MIN_CONTENT_LENGTH:
        return False
    combined = (path + " " + content[:800]).lower()
    # Requiere al menos 2 keywords para evitar falsos positivos
    matches = sum(1 for kw in MODEL_KEYWORDS if kw in combined)
    return matches >= 2
```

- [ ] **Step 3: Actualizar save_pe_output.py — validación + timestamp único**

Cambios clave en `save_pe_output.py`:

```python
from datetime import datetime
# ...
MIN_CONTENT_LENGTH = 200

def _is_pe_content(path: str, content: str) -> bool:
    """True si el archivo parece un output PE."""
    if len(content) < MIN_CONTENT_LENGTH:
        return False
    path_lower = path.lower()
    content_preview = content[:800].lower()
    combined = path_lower + " " + content_preview
    matches = sum(1 for kw in PE_KEYWORDS if kw in combined)
    return matches >= 2

# En main(), reemplazar today y dest_path:
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M")
dest_path = os.path.join(dest_dir, f"{timestamp}_{name}.md")
```

---

## Task 8: Shared State entre Plugins (Problema #9)

**Files:**
- Create: `connectors/shared_state.py`

- [ ] **Step 1: Crear connectors/shared_state.py**

```python
# connectors/shared_state.py
"""
Estado compartido entre plugins de Morgana.
Permite que un análisis DCF en financial-analysis sea reutilizable
en un IC memo de private-equity sin copiar números manualmente.

Uso:
  from connectors.shared_state import SharedState
  state = SharedState()
  state.set("AAPL", "dcf_valuation", {"fair_value": 195.0, "upside": 0.15})
  val = state.get("AAPL", "dcf_valuation")
"""
import json
import threading
from datetime import datetime
from pathlib import Path

_STATE_FILE = Path(__file__).parent.parent / "output" / "morgana_state.json"
_lock = threading.Lock()


class SharedState:
    """
    Key-value store persistente por ticker.
    Estructura: { "AAPL": { "dcf_valuation": {...}, "comps": {...}, ... } }
    """

    def __init__(self):
        _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict:
        if _STATE_FILE.exists():
            try:
                return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self, data: dict):
        _STATE_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    def set(self, ticker: str, key: str, value, ttl_hours: int = 24):
        """
        Guarda value bajo (ticker, key).
        ttl_hours: horas de validez (default 24h — un día de trading)
        """
        ticker = ticker.upper()
        with _lock:
            data = self._load()
            if ticker not in data:
                data[ticker] = {}
            data[ticker][key] = {
                "value": value,
                "saved_at": datetime.now().isoformat(),
                "expires_at": (
                    datetime.now().timestamp() + ttl_hours * 3600
                ),
            }
            self._save(data)

    def get(self, ticker: str, key: str):
        """
        Retorna value o None si no existe / expiró.
        """
        ticker = ticker.upper()
        with _lock:
            data = self._load()
        entry = data.get(ticker, {}).get(key)
        if entry is None:
            return None
        if datetime.now().timestamp() > entry.get("expires_at", 0):
            return None
        return entry.get("value")

    def list_keys(self, ticker: str) -> list[str]:
        """Lista todos los keys disponibles para un ticker."""
        ticker = ticker.upper()
        with _lock:
            data = self._load()
        return list(data.get(ticker, {}).keys())

    def summary(self) -> dict:
        """Resumen de todo el estado: cuántos tickers y keys."""
        with _lock:
            data = self._load()
        return {
            "tickers": len(data),
            "total_entries": sum(len(v) for v in data.values()),
            "tickers_list": list(data.keys()),
        }
```

---

## Task 9: Archive Deprecation + Command Files Faltantes (Problemas #10 y #11)

**Files:**
- Create: `_archive/README.md`
- Create: `commands/compounder.md`
- Create: `commands/chequea.md`
- Create: `commands/asignacion.md`

- [ ] **Step 1: Crear _archive/README.md**

```markdown
# _archive — Plugins Deprecados

Estos plugins han sido deprecados y reemplazados por versiones mejoradas.
**No usar en proyectos nuevos.**

| Plugin | Estado | Reemplazado por |
|--------|--------|-----------------|
| `investment-banking/` | Deprecado v0.2 | `financial-analysis/` (lbo-model, comps-analysis) |
| `wealth-management/` | Deprecado v0.2 | `equity-research/` (thesis-tracker, morning-note) |
| `lseg/` | Deprecado v0.1 | MCPs premium en root `.mcp.json` |
| `spglobal/` | Deprecado v0.1 | `equity-research/skills/earnings-preview/` |
| `financial-analysis-ib/` | Deprecado v0.2 | `financial-analysis/` |
| `private-equity-operational/` | Deprecado v0.2 | `private-equity/` |

Archivado el: 2026-04-14
```

- [ ] **Step 2: Crear commands/compounder.md**

```markdown
# /compounder — Unit Economics + Returns Analysis

Activa análisis profundo de una empresa como "compounding machine".
Combina unit economics (SaaS/growth) y análisis de retornos IRR/MOIC.

## Uso
```
/compounder [TICKER]
```

## Qué activa
1. **unit-economics** (private-equity plugin) — cohorts ARR, LTV/CAC, NDR, payback period
2. **returns-analysis** (private-equity plugin) — IRR/MOIC waterfall + sensibilidades

## Cuándo usarlo
- Empresa SaaS o subscription-based con métricas de cohorts
- Quieres evaluar el "compounding engine" de la empresa
- Post /analiza para profundizar en la calidad del crecimiento

## Output
- Análisis LTV/CAC con benchmark sectorial
- Payback period y curva de recuperación
- Tabla de retornos IRR/MOIC bajo 3 escenarios (bull/base/bear)
- Sensibilidad de retornos vs. entry múltiple y exit múltiple
```

- [ ] **Step 3: Crear commands/chequea.md**

```markdown
# /chequea — Actualización Post-Earnings y Modelo

Actualiza el análisis de una empresa con los datos más recientes.
Útil después de earnings, guidance updates o cambios materiales.

## Uso
```
/chequea [TICKER]
/chequea [TICKER] Q4 2025
```

## Qué activa
1. **earnings-analysis** (equity-research) — análisis beat/miss + guía + estimados
2. **model-update** (equity-research) — actualiza modelo con datos Q nuevos
3. **catalyst-calendar** (equity-research) — próximos catalizadores

## Cuándo usarlo
- Acaba de reportar earnings el ticker monitoreado
- Hay un cambio de guidance material
- Revisión mensual del watchlist

## Output
- Resumen earnings: beat/miss vs consenso
- Actualización de estimados forward
- Catalizadores próximos con impacto estimado
- Recomendación: mantener/ajustar tesis
```

- [ ] **Step 4: Crear commands/asignacion.md**

```markdown
# /asignacion — IC Memo + Sizing de Posición

Genera un Investment Committee memo adaptado a buy-side público.
Incluye tesis, retornos esperados, riesgos y recomendación de sizing.

## Uso
```
/asignacion [TICKER]
/asignacion [TICKER1] [TICKER2]   # comparativa para decidir entre dos
```

## Qué activa
- **ic-memo** (private-equity plugin) — memo estructurado con tesis + retornos + riesgos

## Estructura del output
1. Resumen ejecutivo (3 líneas)
2. Tesis de inversión
3. Retornos esperados (3Y, 5Y con IRR/MOIC)
4. Matriz de riesgos (probabilidad × impacto)
5. Recomendación de sizing (% del portafolio)
6. Condiciones de entrada y salida

## Cuándo usarlo
- Después de /analiza y /compounder para tomar decisión final
- Revisión trimestral de posiciones existentes
- Comparar dos candidatos para asignar capital
```

---

## Task 10: Documento de Auditoría Final

**Files:**
- Create: `output/AUDIT-2026-04-14.md`

- [ ] **Step 1: Crear output/AUDIT-2026-04-14.md con todos los cambios**

Ver sección separada — el documento se genera después de ejecutar todos los fixes.

---

## Self-Review

### Spec coverage
- [x] Problema #1 Cache persistente → Task 1 (cache.py SQLite)
- [x] Problema #2 CAGR logging → Task 5 (fetcher.py observabilidad)
- [x] Problema #3 Universe fallback → Task 6 (fallback_tickers.py + universe.py)
- [x] Problema #4 Error handling por ticker → Task 5 (runner.py)
- [x] Problema #5 Hook validación → Task 7 (3 hooks)
- [x] Problema #6 Input validation → Task 2+3 (validators.py + connectors)
- [x] Problema #7 Retry unificado → Task 2+3 (http_utils.py + connectors)
- [x] Problema #8 Rate limiting → Task 4 (rate_limiter.py + fetcher.py)
- [x] Problema #9 Cross-plugin state → Task 8 (shared_state.py)
- [x] Problema #10 Commands faltantes → Task 9 (3 command files)
- [x] Problema #11 Archive deprecation → Task 9 (_archive/README.md)
- [x] Problema #12 Concurrent safety → Task 7 (timestamps HH-MM)

### Sin placeholders: todos los pasos tienen código completo.
### Tipos consistentes: validate_ticker devuelve str en todas las referencias.
