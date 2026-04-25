import logging
from agents.state import MorganaState
from connectors.perplexity import get_ticker_context

logger = logging.getLogger("morgana.researcher")


def researcher_node(state: MorganaState) -> dict:
    """
    Nodo Researcher: obtiene contexto web via Perplexity.
    Ejecuta 3 búsquedas: noticias, competidores, management.
    Nunca bloquea el flujo aunque Perplexity falle.
    """
    ticker = state["ticker"]
    errors = list(state.get("errors", []))

    try:
        context = get_ticker_context(ticker)
        logger.info("[Researcher] Contexto web obtenido para %s", ticker)
        return {"contexto_web": context, "errors": errors}
    except Exception as exc:
        error_msg = f"[Researcher] Perplexity falló: {exc}"
        logger.warning(error_msg)
        errors.append(error_msg)
        return {"contexto_web": {}, "errors": errors}
