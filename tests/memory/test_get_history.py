from unittest.mock import patch, MagicMock
from memory.get_history import get_last_analysis, get_analysis_count


@patch("memory.get_history.get_supabase")
def test_get_last_analysis_returns_dict(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"ticker": "AAPL", "score_final": 87.0, "decision": "BUY", "date": "2026-04-23"}
    ]
    mock_get_sb.return_value = mock_sb

    result = get_last_analysis("AAPL")

    assert result is not None
    assert result["ticker"] == "AAPL"
    assert result["decision"] == "BUY"


@patch("memory.get_history.get_supabase")
def test_get_last_analysis_returns_none_when_empty(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    mock_get_sb.return_value = mock_sb

    result = get_last_analysis("NEWCO")
    assert result is None


@patch("memory.get_history.get_supabase")
def test_get_analysis_count(mock_get_sb):
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value.count = 5
    mock_get_sb.return_value = mock_sb

    count = get_analysis_count("AAPL")
    assert count == 5
