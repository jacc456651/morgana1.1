from agents.state import MorganaState, initial_state


def test_initial_state_has_required_keys():
    state = initial_state("AAPL", "analiza")
    assert state["ticker"] == "AAPL"
    assert state["command"] == "analiza"
    assert state["datos_financieros"] is None
    assert state["reporte"] is None
    assert state["decision"] is None
    assert state["errors"] == []


def test_initial_state_uppercases_ticker():
    state = initial_state("aapl", "analiza")
    assert state["ticker"] == "AAPL"


def test_state_is_valid_typeddict():
    state: MorganaState = {
        "ticker": "MNDY",
        "command": "analiza",
        "datos_financieros": {"yahoo": {"price": 200}},
        "reporte": "Reporte de prueba",
        "decision": "BUY",
        "errors": [],
    }
    assert state["decision"] == "BUY"
