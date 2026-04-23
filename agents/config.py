import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

BOSS_MODEL = "claude-opus-4-6"
SCOUT_MODEL = "claude-sonnet-4-6"


def get_claude_client() -> Anthropic:
    """
    Devuelve cliente Anthropic. Si PORTKEY_API_KEY está presente,
    enruta llamadas a través de Portkey para caching y observabilidad.
    """
    portkey_key = os.environ.get("PORTKEY_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if portkey_key:
        from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
        return Anthropic(
            api_key=anthropic_key,
            base_url=PORTKEY_GATEWAY_URL,
            default_headers=createHeaders(
                api_key=portkey_key,
                provider="anthropic",
                metadata={"_user": "morgana"}
            )
        )

    return Anthropic(api_key=anthropic_key)
