import pytest

from app.config import get_settings
from app.core.exceptions import ConfigurationError


def test_required_settings_fail_fast(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("EL_TOQUE_API_TOKEN", raising=False)
    get_settings.cache_clear()

    try:
        with pytest.raises(ConfigurationError) as error:
            get_settings()
        assert "database_url" in str(error.value)
        assert "el_toque_api_token" in str(error.value)
    finally:
        get_settings.cache_clear()