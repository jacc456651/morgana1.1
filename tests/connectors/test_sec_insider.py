from datetime import datetime, timedelta
from unittest.mock import patch
from connectors.sec_insider import get_insider_transactions, _parse_form4_filings


SAMPLE_SUBMISSIONS = {
    "filings": {
        "recent": {
            "form": ["4", "10-K", "4", "4", "8-K", "4"],
            "filingDate": [
                datetime.now().strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d"),  # >12 meses
            ],
            "primaryDocDescription": [
                "Statement of changes in beneficial ownership",
                "Annual report",
                "Statement of changes in beneficial ownership",
                "Statement of changes in beneficial ownership",
                "Current report",
                "Statement of changes in beneficial ownership",
            ],
        }
    }
}


def test_parse_form4_counts_within_12_months():
    result = _parse_form4_filings(SAMPLE_SUBMISSIONS)
    # Form 4 en indices 0, 2, 3 están dentro de 12 meses; índice 5 (400 días) queda fuera
    assert result["count_12m"] == 3


def test_parse_form4_returns_recent_dates():
    result = _parse_form4_filings(SAMPLE_SUBMISSIONS)
    assert "recent_dates" in result
    assert len(result["recent_dates"]) <= 5


def test_parse_form4_empty_filings():
    empty = {"filings": {"recent": {"form": [], "filingDate": [], "primaryDocDescription": []}}}
    result = _parse_form4_filings(empty)
    assert result["count_12m"] == 0
    assert result["recent_dates"] == []


@patch("connectors.sec_insider._get_submissions")
@patch("connectors.sec_insider.edgar.get_cik", return_value="0000320193")
def test_get_insider_transactions_returns_dict(mock_cik, mock_subs):
    mock_subs.return_value = SAMPLE_SUBMISSIONS
    result = get_insider_transactions("AAPL")
    assert "count_12m" in result
    assert "recent_dates" in result


@patch("connectors.sec_insider.edgar.get_cik", side_effect=Exception("CIK not found"))
def test_get_insider_transactions_handles_error(mock_cik):
    result = get_insider_transactions("BADTICKER")
    assert isinstance(result, dict)
    assert result.get("count_12m") == 0
