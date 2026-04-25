import logging
from agents.state import MorganaState
from memory.save_analysis import save_analysis, extract_score
from memory.write_report import write_report_md

logger = logging.getLogger("morgana.save")


def save_node(state: MorganaState) -> dict:
    """
    Nodo de persistencia: guarda el análisis en Supabase y escribe el .md.
    Se ejecuta después de Boss. Nunca bloquea el flujo aunque falle.
    """
    ticker = state["ticker"]
    reporte = state.get("reporte") or ""
    decision = state.get("decision") or "HOLD"
    errors = list(state.get("errors", []))
    result = {}

    # Guardar en Supabase
    try:
        analysis_id = save_analysis(
            ticker=ticker,
            command=state.get("command", "analiza"),
            reporte=reporte,
            decision=decision,
            errors=errors,
        )
        if analysis_id:
            result["analysis_id"] = analysis_id
    except Exception as exc:
        logger.warning("[Save] Supabase falló: %s", exc)
        errors.append(f"[Save] Supabase: {exc}")

    # Escribir .md
    try:
        score = extract_score(reporte)
        report_path = write_report_md(
            ticker=ticker,
            reporte=reporte,
            decision=decision,
            score=score,
        )
        result["report_path"] = report_path
        print(f"   [Output] Reporte guardado: {report_path}")
    except Exception as exc:
        logger.warning("[Save] Write .md falló: %s", exc)
        errors.append(f"[Save] Write .md: {exc}")

    result["errors"] = errors
    return result
