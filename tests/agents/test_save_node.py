from unittest.mock import patch
from agents.save_node import save_node
from agents.state import initial_state


@patch("agents.save_node.write_report_md", return_value="output/reportes/AAPL/2026-04-23_analisis.md")
@patch("agents.save_node.save_analysis", return_value="uuid-123")
def test_save_node_persists_analysis(mock_save, mock_write):
    state = initial_state("AAPL", "analiza")
    state["reporte"] = "## AAPL\n**SCORE FINAL: 87/100**\n**DECISION: BUY**"
    state["decision"] = "BUY"
    state["errors"] = []

    result = save_node(state)

    assert mock_save.called
    assert mock_write.called
    assert result.get("analysis_id") == "uuid-123"
    assert result.get("report_path") == "output/reportes/AAPL/2026-04-23_analisis.md"


@patch("agents.save_node.write_report_md", side_effect=Exception("disk full"))
@patch("agents.save_node.save_analysis", return_value="uuid-123")
def test_save_node_continues_on_write_error(mock_save, mock_write):
    state = initial_state("AAPL", "analiza")
    state["reporte"] = "## AAPL"
    state["decision"] = "BUY"
    state["errors"] = []

    result = save_node(state)
    # No debe lanzar excepción
    assert "analysis_id" in result or "errors" in result
