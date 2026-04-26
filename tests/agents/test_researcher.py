from unittest.mock import patch
from agents.researcher import researcher_node
from agents.state import initial_state


@patch("agents.researcher.get_ticker_context", return_value={
    "noticias": "AAPL lanza nuevo iPhone con chip M4",
    "competidores": "Samsung y Google son los principales rivales",
    "management": "Tim Cook enfoca en servicios y AI",
})
def test_researcher_node_adds_web_context(mock_perplexity):
    state = initial_state("AAPL", "analiza")
    result = researcher_node(state)

    assert "contexto_web" in result
    ctx = result["contexto_web"]
    assert "noticias" in ctx
    assert "competidores" in ctx
    assert "management" in ctx


@patch("agents.researcher.get_ticker_context", side_effect=Exception("Perplexity down"))
def test_researcher_node_handles_perplexity_failure(mock_perplexity):
    state = initial_state("AAPL", "analiza")
    result = researcher_node(state)

    # No lanza excepción — retorna contexto vacío o con error
    assert "contexto_web" in result
    assert isinstance(result["contexto_web"], dict)
