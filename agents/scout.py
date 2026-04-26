import sys
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from connectors import edgar, yahoo, finviz, stockanalysis_client, fred, sec_insider, short_interest
from agents.state import MorganaState
from memory.vault_reader import get_vault_context

logger = logging.getLogger("morgana.scout")


def _safe(fn, *args):
    """Ejecuta fn(*args). Devuelve (resultado, None) o (None, mensaje_error)."""
    name = getattr(fn, "__name__", repr(fn))
    try:
        return fn(*args), None
    except Exception as exc:
        logger.warning("Conector falló: %s — %s", name, exc)
        return None, f"{name}: {exc}"


def _df_to_dict(df_or_none):
    """Convierte DataFrame de yfinance a dict serializable (keys a str)."""
    if df_or_none is None:
        return {}
    try:
        raw = df_or_none.to_dict()
        return {
            str(col): {str(idx): val for idx, val in rows.items()}
            if isinstance(rows, dict) else rows
            for col, rows in raw.items()
        }
    except Exception:
        return {}


def scout_node(state: MorganaState) -> dict:
    """
    Recolecta datos financieros de todos los conectores en paralelo.
    Retorna actualizaciones parciales al estado de LangGraph.
    """
    ticker = state["ticker"]
    errors = list(state.get("errors", []))

    tasks = {
        "edgar_10k":    (edgar.get_latest_10k, ticker),
        "edgar_10q":    (edgar.get_latest_10q, ticker),
        "yahoo_info":   (yahoo.get_info, ticker),
        "yahoo_fin":    (yahoo.get_financials, ticker),
        "finviz":       (finviz.get_snapshot, ticker),
        "sa_income":    (stockanalysis_client.get_income_statement, ticker),
        "sa_ratios":    (stockanalysis_client.get_ratios, ticker),
        "fred_macro":   (fred.get_macro_context,),
        "sec_insiders": (sec_insider.get_insider_transactions, ticker),
    }

    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(_safe, fn, *args): key
            for key, (fn, *args) in tasks.items()
        }
        for future in as_completed(futures):
            key = futures[future]
            result, error = future.result()
            if error:
                errors.append(f"[Scout] {error}")
            else:
                results[key] = result

    yahoo_info = results.get("yahoo_info") or {}
    yahoo_fin = results.get("yahoo_fin") or {}

    datos = {
        "edgar": {
            "10k": results.get("edgar_10k") or {},
            "10q": results.get("edgar_10q") or {},
        },
        "yahoo_info": yahoo_info,
        "yahoo_financials": {
            "income_stmt": _df_to_dict(yahoo_fin.get("income_stmt")),
            "balance_sheet": _df_to_dict(yahoo_fin.get("balance_sheet")),
            "cashflow": _df_to_dict(yahoo_fin.get("cashflow")),
        },
        "finviz": results.get("finviz") or {},
        "stockanalysis": {
            "income_statement": results.get("sa_income") or [],
            "ratios": results.get("sa_ratios") or [],
        },
        "macro": results.get("fred_macro") or {},
        "insiders": results.get("sec_insiders") or {},
        "short_interest": short_interest.extract_short_interest(yahoo_info),
    }

    vault = get_vault_context(ticker)
    if vault["count"] > 0:
        logger.info("[Scout] Vault: %d análisis previos para %s", vault["count"], ticker)

    logger.info("[Scout] Recolección completa para %s. Errores: %d", ticker, len(errors))
    return {"datos_financieros": datos, "vault_context": vault, "errors": errors}
