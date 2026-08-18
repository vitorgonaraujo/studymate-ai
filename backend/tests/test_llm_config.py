import pytest

from backend.agent.pdf_agent import resolve_llm_config


def test_groq_uses_official_openai_compatible_endpoint():
    config = resolve_llm_config("groq", "secret")
    assert config.base_url == "https://api.groq.com/openai/v1"
    assert config.api_key == "secret"


def test_gemini_uses_official_openai_compatible_endpoint():
    config = resolve_llm_config("gemini", "secret")
    assert config.base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"


def test_remote_provider_requires_api_key():
    with pytest.raises(ValueError, match="chave de API"):
        resolve_llm_config("groq")


def test_unknown_provider_is_rejected():
    with pytest.raises(ValueError, match="Provedor inválido"):
        resolve_llm_config("unknown", "secret")
