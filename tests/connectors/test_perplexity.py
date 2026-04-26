import os
from unittest.mock import patch, MagicMock
from connectors.perplexity import search_web, get_ticker_context


def _mock_completion(content: str):
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


@patch("connectors.perplexity._get_client")
def test_search_web_returns_string(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_completion("AAPL news: product launch")
    mock_get_client.return_value = mock_client

    result = search_web("AAPL recent news")

    assert isinstance(result, str)
    assert len(result) > 0


@patch("connectors.perplexity._get_client")
def test_get_ticker_context_returns_three_sections(mock_get_client):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = _mock_completion("Context info here")
    mock_get_client.return_value = mock_client

    result = get_ticker_context("AAPL")

    assert "noticias" in result
    assert "competidores" in result
    assert "management" in result


@patch("connectors.perplexity._get_client")
def test_get_ticker_context_handles_error(mock_get_client):
    mock_get_client.side_effect = Exception("API unavailable")

    result = get_ticker_context("AAPL")

    assert isinstance(result, dict)
    # Retorna dict con errores en lugar de lanzar excepción
    assert all(isinstance(v, str) for v in result.values())
