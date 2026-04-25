from typing import TypedDict, Optional


class MorganaState(TypedDict):
    ticker: str
    command: str
    datos_financieros: Optional[dict]
    reporte: Optional[str]
    decision: Optional[str]
    errors: list
    analysis_id: Optional[str]
    report_path: Optional[str]


def initial_state(ticker: str, command: str) -> MorganaState:
    return {
        "ticker": ticker.upper(),
        "command": command,
        "datos_financieros": None,
        "reporte": None,
        "decision": None,
        "errors": [],
        "analysis_id": None,
        "report_path": None,
    }
