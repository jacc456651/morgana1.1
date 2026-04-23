from unittest.mock import patch
from graph.morgana import build_graph
from agents.state import initial_state


def _scout_patch(state):
    return {
        "datos_financieros": {"yahoo_info": {"currentPrice": 200.0}, "finviz": {"P/E": "25"}},
        "errors": [],
    }


def _boss_patch(state):
    return {
        "reporte": "## AAPL\n**SCORE FINAL: 85/100 — COMPOUNDER ELITE**\n**DECISION: BUY**\n### Tesis\nMoat expansivo.\n### Antitesis\nSaturacion hardware.",
        "decision": "BUY",
        "errors": [],
    }


@patch("graph.morgana.boss_node", side_effect=_boss_patch)
@patch("graph.morgana.scout_node", side_effect=_scout_patch)
def test_graph_runs_scout_then_boss(mock_scout, mock_boss):
    graph = build_graph()
    state = initial_state("AAPL", "analiza")
    result = graph.invoke(state)

    assert mock_scout.called
    assert mock_boss.called
    assert result["decision"] == "BUY"
    assert result["datos_financieros"] is not None
    assert result["reporte"] is not None


@patch("graph.morgana.boss_node", side_effect=_boss_patch)
@patch("graph.morgana.scout_node", side_effect=_scout_patch)
def test_graph_preserves_ticker(mock_scout, mock_boss):
    graph = build_graph()
    state = initial_state("MNDY", "analiza")
    result = graph.invoke(state)
    assert result["ticker"] == "MNDY"
