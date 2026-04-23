from unittest.mock import patch, MagicMock
from agents.boss import boss_node, _extract_decision
from agents.state import initial_state


def _mock_response(text: str):
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


SAMPLE_REPORT = """
## AAPL — Apple Inc. | Analisis Morgana

**SCORE FINAL: 87/100 — COMPOUNDER ELITE**
**ETAPA:** Compounder
**DECISION: BUY**

### P1 — MOAT DINAMICO | Score: 9/10
Ecosistema Apple genera switching costs masivos.

### P2 — FINANZAS GROWTH | Score: 8/10
FCF conversion >95%. ROIC consistente >30%.

### P3 — MOTOR DE CRECIMIENTO | Score: 8/10
Servicios creciendo 15%+ anual con penetracion <20% del TAM global.

### P4 — MANAGEMENT | Score: 9/10
Tim Cook. Insider ownership. Buybacks disciplinados a precios razonables.

### P5 — CONTEXTO | Score: 9/10
PEG <1.5. Institucionales acumulando. AI edge en dispositivos.

### Tesis
Apple es una maquina de compounding con moat expandiendose en servicios.

### Antitesis
Saturacion del mercado de smartphones puede limitar el crecimiento de hardware.

### Decision
**BUY** — Entrada ideal por debajo de $200.
"""


def test_extract_decision_buy():
    assert _extract_decision("... **BUY** ...") == "BUY"


def test_extract_decision_hold():
    assert _extract_decision("... **HOLD** ...") == "HOLD"


def test_extract_decision_avoid():
    assert _extract_decision("... **AVOID** ...") == "AVOID"


def test_extract_decision_fallback():
    assert _extract_decision("no decision here") == "HOLD"


@patch("agents.boss.get_claude_client")
def test_boss_node_returns_report_and_decision(mock_get_client):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(SAMPLE_REPORT)
    mock_get_client.return_value = mock_client

    state = initial_state("AAPL", "analiza")
    state["datos_financieros"] = {"yahoo_info": {"currentPrice": 210.0}, "finviz": {"P/E": "28"}}

    result = boss_node(state)

    assert "reporte" in result
    assert "decision" in result
    assert result["decision"] in ("BUY", "HOLD", "AVOID")
    assert len(result["reporte"]) > 100


@patch("agents.boss.get_claude_client")
def test_boss_node_calls_opus_model(mock_get_client):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _mock_response(SAMPLE_REPORT)
    mock_get_client.return_value = mock_client

    state = initial_state("AAPL", "analiza")
    state["datos_financieros"] = {}

    boss_node(state)

    call_kwargs = mock_client.messages.create.call_args[1]
    assert "opus" in call_kwargs["model"].lower()


@patch("agents.boss.get_claude_client")
def test_boss_node_handles_api_error(mock_get_client):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("API timeout")
    mock_get_client.return_value = mock_client

    state = initial_state("AAPL", "analiza")
    state["datos_financieros"] = {}

    result = boss_node(state)

    assert result["decision"] == "ERROR"
    assert len(result["errors"]) > 0
