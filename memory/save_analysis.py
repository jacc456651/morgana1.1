import re
import logging
from memory.supabase_client import get_supabase

logger = logging.getLogger("morgana.memory")


def extract_score(reporte: str) -> float | None:
    match = re.search(r"SCORE FINAL:\s*(\d+(?:\.\d+)?)/100", reporte)
    return float(match.group(1)) if match else None


def extract_classification(reporte: str) -> str | None:
    match = re.search(
        r"SCORE FINAL:.*?—\s*(COMPOUNDER ELITE|HIGH GROWTH|WATCHLIST|DESCARTAR)",
        reporte
    )
    return match.group(1) if match else None


def extract_stage(reporte: str) -> str | None:
    match = re.search(r"\*\*ETAPA:\*\*\s*(Early Growth|Scaling|Compounder)", reporte)
    return match.group(1) if match else None


def save_analysis(
    ticker: str, command: str, reporte: str, decision: str, errors: list
) -> str | None:
    """Guarda el análisis en Supabase. Retorna el UUID generado o None si falla."""
    try:
        sb = get_supabase()
        result = sb.table("analyses").insert({
            "ticker": ticker,
            "command": command,
            "score_final": extract_score(reporte),
            "classification": extract_classification(reporte),
            "stage": extract_stage(reporte),
            "decision": decision,
            "reporte": reporte,
            "errors": errors,
        }).execute()

        if result.data:
            analysis_id = result.data[0]["id"]
            logger.info("[Supabase] Análisis guardado: %s → %s", ticker, analysis_id)
            return analysis_id

    except Exception as exc:
        logger.warning("[Supabase] Error guardando análisis: %s", exc)

    return None
