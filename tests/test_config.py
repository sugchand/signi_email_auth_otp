from signi_email_otp import config
import pytest


def test_db_uri():
    assert hasattr(config, "DB_URL")
    assert isinstance(config.DB_URL, str)
    assert (
        config.DB_URL.startswith("sqlite://") or 
        config.DB_URL.startswith("postgresql://")
        )


def test_otp_expiry_seconds():
    assert hasattr(config, "OTP_EXPIRY_SECONDS")
    assert isinstance(config.OTP_EXPIRY_SECONDS, int)
    assert config.OTP_EXPIRY_SECONDS > 0


def test_jwt_expiry_seconds():
    assert hasattr(config, "JWT_EXPIRY_SECONDS")
    assert isinstance(config.JWT_EXPIRY_SECONDS, int)
    assert config.JWT_EXPIRY_SECONDS > 0


def test_jwt_secret():
    assert hasattr(config, "JWT_SECRET")
    assert isinstance(config.JWT_SECRET, str)
    assert len(config.JWT_SECRET) > 0


def test_email_from():
    assert hasattr(config, "SMTP_FROM_EMAIL")
    assert isinstance(config.SMTP_FROM_EMAIL, str)
    assert "@" in config.SMTP_FROM_EMAIL


def test_smtp_emai_pwd():
    assert hasattr(config, "SMTP_FROM_PASSWORD")
    assert isinstance(config.SMTP_FROM_PASSWORD, str)
    assert len(config.SMTP_FROM_PASSWORD) > 0


def test_smtp_host():
    assert hasattr(config, "SMTP_HOST")
    assert isinstance(config.SMTP_HOST, str)
    assert len(config.SMTP_HOST) > 0


def test_smtp_port():
    assert hasattr(config, "SMTP_PORT")
    assert isinstance(config.SMTP_PORT, int)
    assert config.SMTP_PORT > 0


def test_max_conn():
    assert hasattr(config, "MAX_CONN")
    assert isinstance(config.MAX_CONN, int)
    assert config.MAX_CONN > 0


def test_get_env_returns_env_value(monkeypatch):
    monkeypatch.setenv("TEST_ENV_VAR", "test_value")
    assert config.get_env("TEST_ENV_VAR") == "test_value"


def test_get_env_returns_default(monkeypatch):
    monkeypatch.delenv("TEST_ENV_VAR", raising=False)
    assert config.get_env("TEST_ENV_VAR", 
                          default="default_value") == "default_value"


def test_get_env_raises_if_missing_and_no_default(monkeypatch):
    monkeypatch.delenv("TEST_ENV_VAR", raising=False)
    with pytest.raises(KeyError):
        config.get_env("TEST_ENV_VAR")