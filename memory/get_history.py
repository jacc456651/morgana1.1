import logging
from memory.supabase_client import get_supabase

logger = logging.getLogger("morgana.history")


def get_last_analysis(ticker: str) -> dict | None:
    """Recupera el análisis más reciente de un ticker desde Supabase."""
    try:
        sb = get_supabase()
        result = (
            sb.table("analyses")
            .select("*")
            .eq("ticker", ticker.upper())
            .order("date", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
    except Exception as exc:
        logger.warning("[History] Error recuperando análisis de %s: %s", ticker, exc)
    return None


def get_analysis_count(ticker: str) -> int:
    """Cuenta cuántos análisis existen para un ticker."""
    try:
        sb = get_supabase()
        result = (
            sb.table("analyses")
            .select("id", count="exact")
            .eq("ticker", ticker.upper())
            .execute()
        )
        return result.count or 0
    except Exception as exc:
        logger.warning("[History] Error contando análisis de %s: %s", ticker, exc)
        return 0
