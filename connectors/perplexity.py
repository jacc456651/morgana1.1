"""
Connector para Perplexity API.
Usa la API compatible con OpenAI. Requiere PERPLEXITY_API_KEY en .env.
"""
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logger = logging.getLogger("morgana.perplexity")

PERPLEXITY_BASE_URL = "https://api.perplexity.ai"
MODEL = "llama-3.1-sonar-large-128k-online"


def _get_client() -> OpenAI:
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY requerida en .env")
    return OpenAI(api_key=api_key, base_url=PERPLEXITY_BASE_URL)


def search_web(query: str, max_tokens: int = 800) -> str:
    """Ejecuta una búsqueda web via Perplexity. Retorna texto con fuentes."""
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente de investigación financiera. Responde en español, con datos concretos y cita las fuentes cuando sea posible.",
            },
            {"role": "user", "content": query},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def get_ticker_context(ticker: str) -> dict:
    """
    Ejecuta 3 búsquedas específicas para un ticker.
    Retorna dict con: noticias, competidores, management.
    Nunca lanza excepción — retorna strings vacíos si falla.
    """
    queries = {
        "noticias": f"{ticker} stock news earnings results last 30 days 2026",
        "competidores": f"{ticker} competitors market share competitive landscape 2026",
        "management": f"{ticker} CEO management team recent decisions strategy 2026",
    }

    context = {}
    for key, query in queries.items():
        try:
            context[key] = search_web(query)
            logger.info("[Perplexity] Query '%s' para %s OK", key, ticker)
        except Exception as exc:
            logger.warning("[Perplexity] Query '%s' falló: %s", key, exc)
            context[key] = f"No disponible ({exc})"

    return context
