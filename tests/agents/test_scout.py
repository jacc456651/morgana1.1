from unittest.mock import patch, MagicMock
from agents.scout import scout_node
from agents.state import initial_state


def _make_mock_df():
    """DataFrame mock con método to_dict()."""
    mock = MagicMock()
    mock.to_dict.return_value = {"Revenue": {"2024": 391_000_000_000}}
    return mock


def _mock_financials(mock_fin):
    mock_df = _make_mock_df()
    mock_fin.return_value = {
        "income_stmt": mock_df,
        "balance_sheet": mock_df,
        "cashflow": mock_df,
    }


# Decoradores comunes para los 3 conectores nuevos (evitan llamadas HTTP reales en tests)
_NEW_CONNECTORS = [
    patch("agents.scout.short_interest.extract_short_interest", return_value={"short_percent_of_float": 0.007}),
    patch("agents.scout.sec_insider.get_insider_transactions", return_value={"count_12m": 3, "recent_dates": []}),
    patch("agents.scout.fred.get_macro_context", return_value={"fed_funds_rate": 5.33, "treasury_10y": 4.5, "cpi": 315.2, "unemployment": 4.1, "gdp": 29000.0}),
]


@patch("agents.scout.short_interest.extract_short_interest", return_value={"short_percent_of_float": 0.007})
@patch("agents.scout.sec_insider.get_insider_transactions", return_value={"count_12m": 3, "recent_dates": []})
@patch("agents.scout.fred.get_macro_context", return_value={"fed_funds_rate": 5.33, "treasury_10y": 4.5, "cpi": 315.2, "unemployment": 4.1, "gdp": 29000.0})
@patch("agents.scout.stockanalysis_client.get_ratios", return_value=[{"metric": "ROE", "2024": "25%"}])
@patch("agents.scout.stockanalysis_client.get_income_statement", return_value=[{"metric": "Revenue", "2024": "391B"}])
@patch("agents.scout.finviz.get_snapshot", return_value={"P/E": "28.5", "ROE": "25%", "Sector": "Technology"})
@patch("agents.scout.yahoo.get_financials")
@patch("agents.scout.yahoo.get_info", return_value={"currentPrice": 210.0, "marketCap": 3_000_000_000_000, "trailingPE": 28.5})
@patch("agents.scout.edgar.get_latest_10q", return_value={"form": "10-Q", "date": "2024-12-31"})
@patch("agents.scout.edgar.get_latest_10k", return_value={"form": "10-K", "date": "2024-09-30", "url": "https://sec.gov/..."})
def test_scout_collects_all_sources(mock_10k, mock_10q, mock_info, mock_financials, mock_finviz, mock_income, mock_ratios, mock_fred, mock_insiders, mock_si):
    _mock_financials(mock_financials)

    state = initial_state("AAPL", "analiza")
    result = scout_node(state)

    assert "datos_financieros" in result
    datos = result["datos_financieros"]
    assert "edgar" in datos
    assert "yahoo_info" in datos
    assert "finviz" in datos
    assert "stockanalysis" in datos
    assert datos["edgar"]["10k"]["form"] == "10-K"
    assert datos["yahoo_info"]["currentPrice"] == 210.0
    assert datos["finviz"]["P/E"] == "28.5"


@patch("agents.scout.short_interest.extract_short_interest", return_value={})
@patch("agents.scout.sec_insider.get_insider_transactions", return_value={"count_12m": 0, "recent_dates": []})
@patch("agents.scout.fred.get_macro_context", return_value={})
@patch("agents.scout.edgar.get_latest_10k", side_effect=Exception("SEC timeout"))
@patch("agents.scout.edgar.get_latest_10q", return_value={})
@patch("agents.scout.yahoo.get_info", return_value={"currentPrice": 210.0})
@patch("agents.scout.yahoo.get_financials")
@patch("agents.scout.finviz.get_snapshot", return_value={})
@patch("agents.scout.stockanalysis_client.get_income_statement", return_value=[])
@patch("agents.scout.stockanalysis_client.get_ratios", return_value=[])
def test_scout_handles_connector_error(mock_r, mock_i, mock_fv, mock_fin, mock_info, mock_10q, mock_10k, mock_fred, mock_insiders, mock_si):
    mock_df = MagicMock()
    mock_df.to_dict.return_value = {}
    mock_fin.return_value = {"income_stmt": mock_df, "balance_sheet": mock_df, "cashflow": mock_df}

    state = initial_state("AAPL", "analiza")
    result = scout_node(state)

    assert "datos_financieros" in result
    assert len(result.get("errors", [])) > 0


@patch("agents.scout.short_interest.extract_short_interest", return_value={"short_percent_of_float": 0.007})
@patch("agents.scout.sec_insider.get_insider_transactions", return_value={"count_12m": 5, "recent_dates": []})
@patch("agents.scout.fred.get_macro_context", return_value={"fed_funds_rate": 5.33, "treasury_10y": 4.5, "cpi": 315.2, "unemployment": 4.1, "gdp": 29000.0})
@patch("agents.scout.stockanalysis_client.get_ratios", return_value=[])
@patch("agents.scout.stockanalysis_client.get_income_statement", return_value=[])
@patch("agents.scout.finviz.get_snapshot", return_value={})
@patch("agents.scout.yahoo.get_financials")
@patch("agents.scout.yahoo.get_info", return_value={"currentPrice": 210.0, "shortPercentOfFloat": 0.007})
@patch("agents.scout.edgar.get_latest_10q", return_value={})
@patch("agents.scout.edgar.get_latest_10k", return_value={})
def test_scout_includes_macro_insiders_short_interest(
    mock_10k, mock_10q, mock_info, mock_financials, mock_finviz,
    mock_income, mock_ratios, mock_fred, mock_insiders, mock_si
):
    mock_df = MagicMock()
    mock_df.to_dict.return_value = {}
    mock_financials.return_value = {"income_stmt": mock_df, "balance_sheet": mock_df, "cashflow": mock_df}

    state = initial_state("AAPL", "analiza")
    result = scout_node(state)

    datos = result["datos_financieros"]
    assert "macro" in datos
    assert "insiders" in datos
    assert "short_interest" in datos
    assert datos["macro"]["fed_funds_rate"] == 5.33
    assert datos["insiders"]["count_12m"] == 5
    assert datos["short_interest"]["short_percent_of_float"] == 0.007


@patch("agents.scout.short_interest.extract_short_interest", return_value={})
@patch("agents.scout.sec_insider.get_insider_transactions", side_effect=Exception("SEC timeout"))
@patch("agents.scout.fred.get_macro_context", side_effect=Exception("FRED down"))
@patch("agents.scout.stockanalysis_client.get_ratios", return_value=[])
@patch("agents.scout.stockanalysis_client.get_income_statement", return_value=[])
@patch("agents.scout.finviz.get_snapshot", return_value={})
@patch("agents.scout.yahoo.get_financials")
@patch("agents.scout.yahoo.get_info", return_value={"currentPrice": 210.0})
@patch("agents.scout.edgar.get_latest_10q", return_value={})
@patch("agents.scout.edgar.get_latest_10k", return_value={})
def test_scout_degrades_gracefully_when_new_connectors_fail(
    mock_10k, mock_10q, mock_info, mock_financials, mock_finviz,
    mock_income, mock_ratios, mock_fred, mock_insiders, mock_si
):
    mock_df = MagicMock()
    mock_df.to_dict.return_value = {}
    mock_financials.return_value = {"income_stmt": mock_df, "balance_sheet": mock_df, "cashflow": mock_df}

    state = initial_state("AAPL", "analiza")
    result = scout_node(state)

    assert "datos_financieros" in result
    assert len(result.get("errors", [])) > 0
