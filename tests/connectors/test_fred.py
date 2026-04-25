from unittest.mock import patch, MagicMock
from connectors.fred import get_series_latest, get_macro_context


def _mock_fred_obs(value: str, date: str = "2026-04-01"):
    return {"observations": [{"date": date, "value": value}]}


@patch("connectors.fred._get")
def test_get_series_latest_returns_float(mock_get):
    mock_get.return_value = _mock_fred_obs("5.33")
    result = get_series_latest("DFF")
    assert result == 5.33


@patch("connectors.fred._get")
def test_get_series_latest_returns_none_for_missing_value(mock_get):
    mock_get.return_value = _mock_fred_obs(".")
    result = get_series_latest("DFF")
    assert result is None


@patch("connectors.fred._get")
def test_get_series_latest_returns_none_on_error(mock_get):
    mock_get.side_effect = Exception("FRED down")
    result = get_series_latest("DFF")
    assert result is None


@patch("connectors.fred._get")
def test_get_macro_context_returns_all_keys(mock_get):
    mock_get.return_value = _mock_fred_obs("5.33")
    result = get_macro_context()
    assert "fed_funds_rate" in result
    assert "treasury_10y" in result
    assert "cpi" in result
    assert "unemployment" in result
    assert "gdp" in result


@patch("connectors.fred._get")
def test_get_macro_context_handles_partial_failure(mock_get):
    mock_get.side_effect = [Exception("timeout"), _mock_fred_obs("4.5")] * 5
    result = get_macro_context()
    assert isinstance(result, dict)
    assert len(result) == 5
