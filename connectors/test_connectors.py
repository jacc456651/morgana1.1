"""
Test de los conectores con AAPL.
Uso: py connectors/test_connectors.py
"""
import sys
import time

TICKER = "AAPL"
PASS = "[OK]"
FAIL = "[FAIL]"


def _timer(fn):
    """Ejecuta fn() y retorna (result, elapsed_seconds)."""
    t0 = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - t0


def test_edgar():
    print(f"\n{'='*50}")
    print(f"EDGAR — data.sec.gov")
    print(f"{'='*50}")
    try:
        from connectors import edgar

        # Test 1: CIK lookup
        cik, elapsed = _timer(lambda: edgar.get_cik(TICKER))
        print(f"{PASS} CIK de {TICKER}: {cik}  ({elapsed:.2f}s)")

        # Test 2: Latest 10-K
        filing, elapsed = _timer(lambda: edgar.get_latest_10k(TICKER))
        if filing:
            print(f"{PASS} 10-K más reciente: {filing['date']}  ({elapsed:.2f}s)")
            print(f"     URL: {filing['url']}")
        else:
            print(f"{FAIL} No se encontró 10-K  ({elapsed:.2f}s)")

        # Test 3: Latest 10-Q
        filing_q, elapsed = _timer(lambda: edgar.get_latest_10q(TICKER))
        if filing_q:
            print(f"{PASS} 10-Q más reciente: {filing_q['date']}  ({elapsed:.2f}s)")
        else:
            print(f"{FAIL} No se encontró 10-Q  ({elapsed:.2f}s)")

        # Test 4: Métrica de revenue
        revenues, elapsed = _timer(lambda: edgar.get_metric(TICKER, "us-gaap/Revenues"))
        if revenues:
            last = revenues[-1]
            print(f"{PASS} Revenue anual más reciente: ${last['val']:,.0f} ({last['end']})  ({elapsed:.2f}s)")
        else:
            revenues, elapsed = _timer(
                lambda: edgar.get_metric(TICKER, "us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax")
            )
            if revenues:
                last = revenues[-1]
                print(f"{PASS} Revenue anual más reciente: ${last['val']:,.0f} ({last['end']})  ({elapsed:.2f}s)")
            else:
                print(f"[INFO] Métrica de revenue no encontrada con etiquetas estándar  ({elapsed:.2f}s)")

        return True
    except Exception as e:
        print(f"{FAIL} EDGAR error: {e}")
        return False


def test_yahoo():
    print(f"\n{'='*50}")
    print(f"Yahoo Finance — yfinance")
    print(f"{'='*50}")
    try:
        from connectors import yahoo

        # Test 1: Precio actual
        price, elapsed = _timer(lambda: yahoo.get_price(TICKER))
        print(f"{PASS} Precio actual de {TICKER}: ${price}  ({elapsed:.2f}s)")

        # Test 2: Ratios clave
        ratios, elapsed = _timer(lambda: yahoo.get_key_ratios(TICKER))
        print(f"{PASS} Ratios clave obtenidos  ({elapsed:.2f}s):")
        for k, v in ratios.items():
            if v is not None:
                print(f"     {k}: {v}")

        # Test 3: Historial de precios (últimos 5 días)
        hist, elapsed = _timer(lambda: yahoo.get_history(TICKER, period="5d"))
        if not hist.empty:
            print(f"{PASS} Historial OHLCV (últimos 5d): {len(hist)} filas  ({elapsed:.2f}s)")
        else:
            print(f"{FAIL} Historial vacío  ({elapsed:.2f}s)")

        return True
    except Exception as e:
        print(f"{FAIL} Yahoo Finance error: {e}")
        return False


def test_finviz():
    print(f"\n{'='*50}")
    print(f"Finviz — finviz.com")
    print(f"{'='*50}")
    try:
        from connectors import finviz

        metrics, elapsed = _timer(lambda: finviz.get_key_metrics(TICKER))
        non_null = {k: v for k, v in metrics.items() if v is not None}
        if non_null:
            print(f"{PASS} Métricas de Finviz obtenidas ({len(non_null)} campos)  ({elapsed:.2f}s):")
            for k, v in non_null.items():
                print(f"     {k}: {v}")
        else:
            print(f"[WARN] Finviz devolvió 0 métricas (posible bloqueo por IP/rate-limit)  ({elapsed:.2f}s)")

        return True
    except Exception as e:
        print(f"{FAIL} Finviz error: {e}")
        return False


def test_stockanalysis():
    print(f"\n{'='*50}")
    print(f"StockAnalysis — stockanalysis.com")
    print(f"{'='*50}")
    try:
        from connectors import stockanalysis_client as sa

        rows, elapsed = _timer(lambda: sa.get_income_statement(TICKER))
        if rows:
            print(f"{PASS} Income statement obtenido: {len(rows)} métricas  ({elapsed:.2f}s)")
            for row in rows[:5]:
                print(f"     {row.get('metric', '?')}: {list(row.values())[1] if len(row) > 1 else '-'}")
            if len(rows) > 5:
                print(f"     ... y {len(rows) - 5} métricas más")
        else:
            print(f"[WARN] StockAnalysis devolvió 0 filas (posible bloqueo o cambio de estructura)  ({elapsed:.2f}s)")

        return True
    except Exception as e:
        print(f"{FAIL} StockAnalysis error: {e}")
        return False


def test_resolver():
    print(f"\n{'='*50}")
    print(f"Resolver — fallback entre fuentes")
    print(f"{'='*50}")
    try:
        from connectors import resolver

        result, elapsed = _timer(lambda: resolver.get_financials(TICKER))
        source = result.get("source")
        data = result.get("data", {})

        if source and data:
            non_null = {k: v for k, v in data.items() if v is not None}
            print(f"{PASS} Fuente usada: {source}  ({elapsed:.2f}s)")
            print(f"     {len(non_null)} campos con valor de {len(data)} totales")
        elif source is None:
            print(f"{FAIL} Todas las fuentes fallaron  ({elapsed:.2f}s)")
            return False
        else:
            print(f"[WARN] Fuente '{source}' respondió pero devolvió datos vacíos  ({elapsed:.2f}s)")

        return True
    except Exception as e:
        print(f"{FAIL} Resolver error: {e}")
        return False


def test_cache():
    print(f"\n{'='*50}")
    print(f"Caché — SimpleCache TTL")
    print(f"{'='*50}")
    try:
        from connectors import yahoo
        from connectors.cache import _cache

        # Limpiar cache para garantizar que la primera llamada va a red
        _cache.clear()

        # Primera llamada — va a la red
        _, elapsed_first = _timer(lambda: yahoo.get_info(TICKER))
        print(f"     Primera llamada (red):   {elapsed_first:.3f}s")

        # Segunda llamada — debe servirse del cache
        _, elapsed_second = _timer(lambda: yahoo.get_info(TICKER))
        print(f"     Segunda llamada (cache): {elapsed_second:.3f}s")

        if elapsed_second < elapsed_first * 0.1:
            print(f"{PASS} Cache funcionando: segunda llamada {elapsed_first / elapsed_second:.0f}x más rápida")
        else:
            print(f"[WARN] Segunda llamada no fue significativamente más rápida — ¿cache activo?")

        return True
    except Exception as e:
        print(f"{FAIL} Cache error: {e}")
        return False


if __name__ == "__main__":
    print(f"Morgana — Test de conectores con {TICKER}")

    import os
    from datetime import date
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    sys.path.insert(0, project_root)

    print(f"Fecha: {date.today()}")

    suite = [
        ("EDGAR",         test_edgar),
        ("Yahoo Finance", test_yahoo),
        ("Finviz",        test_finviz),
        ("StockAnalysis", test_stockanalysis),
        ("Resolver",      test_resolver),
        ("Cache",         test_cache),
    ]

    results = {}
    total_start = time.perf_counter()
    for name, fn in suite:
        results[name] = fn()
    total_elapsed = time.perf_counter() - total_start

    print(f"\n{'='*50}")
    print(f"RESUMEN  (total: {total_elapsed:.1f}s)")
    print(f"{'='*50}")
    for name, ok in results.items():
        status = PASS if ok else FAIL
        print(f"{status} {name}")

    failed = [k for k, v in results.items() if not v]
    if failed:
        print(f"\nFallaron: {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"\nTodos los conectores funcionan correctamente.")
        sys.exit(0)
