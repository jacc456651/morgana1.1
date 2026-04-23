from typing import TypedDict, Optional


class MorganaState(TypedDict):
    ticker: str
    command: str
    datos_financieros: Optional[dict]
    reporte: Optional[str]
    decision: Optional[str]
    errors: list


def initial_state(ticker: str, command: str) -> MorganaState:
    return {
        "ticker": ticker.upper(),
        "command": command,
        "datos_financieros": None,
        "reporte": None,
        "decision": None,
        "errors": [],
    }
