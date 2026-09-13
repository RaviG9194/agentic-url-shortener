from app.config import OPENAI_MODEL, is_llm_available


def test_default_openai_model():
    assert OPENAI_MODEL


def test_llm_availability_without_api_key(monkeypatch):
    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )

    # Reload the module after removing the environment variable.
    import importlib
    import app.config

    importlib.reload(app.config)

    assert app.config.is_llm_available() is False
