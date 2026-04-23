import os
from unittest.mock import patch
from agents.config import get_claude_client, BOSS_MODEL, SCOUT_MODEL


def test_boss_model_is_opus():
    assert "opus" in BOSS_MODEL.lower()


def test_scout_model_is_sonnet():
    assert "sonnet" in SCOUT_MODEL.lower()


def test_get_client_without_portkey_returns_anthropic():
    env = {"ANTHROPIC_API_KEY": "test-key"}
    with patch.dict(os.environ, env):
        os.environ.pop("PORTKEY_API_KEY", None)
        client = get_claude_client()
        assert client is not None


def test_get_client_with_portkey_returns_client(monkeypatch):
    monkeypatch.setenv("PORTKEY_API_KEY", "test-portkey-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    client = get_claude_client()
    assert client is not None
