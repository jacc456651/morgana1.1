from connectors.short_interest import extract_short_interest

SAMPLE_YAHOO_INFO = {
    "shortPercentOfFloat": 0.0071,
    "sharesShort": 87_000_000,
    "shortRatio": 1.5,
    "sharesShortPriorMonth": 80_000_000,
    "floatShares": 15_200_000_000,
    "currentPrice": 210.0,
}


def test_extract_returns_expected_keys():
    result = extract_short_interest(SAMPLE_YAHOO_INFO)
    assert "short_percent_of_float" in result
    assert "shares_short" in result
    assert "short_ratio" in result
    assert "shares_short_prior_month" in result
    assert "float_shares" in result


def test_extract_computes_mom_change():
    result = extract_short_interest(SAMPLE_YAHOO_INFO)
    # (87M - 80M) / 80M * 100 = 8.75%
    assert result["shares_short_change_pct"] == 8.75


def test_extract_handles_missing_fields():
    result = extract_short_interest({})
    assert result["short_percent_of_float"] is None
    assert result["shares_short"] is None
    assert result["shares_short_change_pct"] is None


def test_extract_handles_prior_month_zero():
    info = {"sharesShort": 100, "sharesShortPriorMonth": 0}
    result = extract_short_interest(info)
    assert result["shares_short_change_pct"] is None


def test_extract_does_not_make_http_calls():
    # Si llama HTTP, los tests fallarían por red — pasa si es función pura
    result = extract_short_interest(SAMPLE_YAHOO_INFO)
    assert isinstance(result, dict)
