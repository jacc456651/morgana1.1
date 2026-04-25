import os
from unittest.mock import patch
import pytest
from memory.supabase_client import get_supabase


def test_get_supabase_raises_without_url():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="SUPABASE_URL"):
            get_supabase()


def test_get_supabase_raises_without_key(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    with pytest.raises(ValueError, match="SUPABASE_ANON_KEY"):
        get_supabase()


def test_get_supabase_returns_client(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
    client = get_supabase()
    assert client is not None
