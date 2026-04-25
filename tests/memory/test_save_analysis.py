from unittest.mock import patch, MagicMock
from memory.save_analysis import extract_score, extract_classification, save_analysis

SAMPLE_REPORT = """
## AAPL — Apple Inc. | Analisis Morgana

**SCORE FINAL: 87/100 — COMPOUNDER ELITE**
**ETAPA:** Compounder
**DECISION: BUY**

### P1 — MOAT DINAMICO | Score: 9/10
Moat expansivo via ecosistema.
"""


def test_extract_score_from_report():
    assert extract_score(SAMPLE_REPORT) == 87.0


def test_extract_score_returns_none_when_missing():
    assert extract_score("reporte sin score") is None


def test_extract_classification_compounder_elite():
    assert extract_classification(SAMPLE_REPORT) == "COMPOUNDER ELITE"


def test_extract_classification_high_growth():
    report = "**SCORE FINAL: 75/100 — HIGH GROWTH**"
    assert extract_classification(report) == "HIGH GROWTH"


def test_extract_classification_watchlist():
    report = "**SCORE FINAL: 65/100 — WATCHLIST**"
    assert extract_classification(report) == "WATCHLIST"


def test_extract_classification_descartar():
    report = "**SCORE FINAL: 50/100 — DESCARTAR**"
    assert extract_classification(report) == "DESCARTAR"


@patch("memory.save_analysis.get_supabase")
def test_save_analysis_returns_id(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.insert.return_value.execute.return_value.data = [
        {"id": "test-uuid-123"}
    ]
    mock_get_sb.return_value = mock_sb

    result = save_analysis("AAPL", "analiza", SAMPLE_REPORT, "BUY", [])

    assert result == "test-uuid-123"
    mock_sb.table.assert_called_with("analyses")


@patch("memory.save_analysis.get_supabase")
def test_save_analysis_returns_none_on_error(mock_get_sb):
    mock_get_sb.side_effect = Exception("DB connection failed")

    result = save_analysis("AAPL", "analiza", SAMPLE_REPORT, "BUY", [])

    assert result is None
