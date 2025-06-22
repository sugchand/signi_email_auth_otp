import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

from signi_email_otp import auth
from signi_email_otp.auth import RateLimitOTPExceededException

EMAIL = "user@example.com"


@pytest.fixture
def mock_session():
    class DummyResult:
        def __init__(self, row=None):
            self._row = row

        def fetchone(self):
            return self._row

    session = MagicMock()
    session.execute.return_value = DummyResult()
    return session


@patch("signi_email_otp.auth.get_db")
@patch("signi_email_otp.auth.random.randint")
def test_request_otp_new(mock_randint, mock_get_db):
    mock_randint.return_value = 123456

    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None  # Simulate no existing OTP

    mock_session.execute.return_value = mock_result
    mock_get_db.return_value.__enter__.return_value = mock_session

    otp = auth.request_otp(EMAIL)
    assert otp == "123456"
    assert mock_session.execute.call_count == 2  # SELECT + INSERT


@patch("signi_email_otp.auth.get_db")
@patch("signi_email_otp.auth.random.randint")
def test_request_otp_reuse_valid(mock_randint, mock_get_db):
    mock_randint.return_value = 654321

    mock_session = MagicMock()
    mock_result = MagicMock()
    created_at = datetime.now(timezone.utc) - timedelta(seconds=10)
    mock_result.fetchone.return_value = ("111111", created_at, 2)

    mock_session.execute.return_value = mock_result
    mock_get_db.return_value.__enter__.return_value = mock_session

    otp = auth.request_otp(EMAIL)
    assert otp == "111111"
    assert mock_session.execute.call_count == 2  # SELECT + UPDATE


@patch("signi_email_otp.auth.get_db")
@patch("signi_email_otp.auth.random.randint")
def test_request_otp_expired(mock_randint, mock_get_db):
    mock_randint.return_value = 222222

    mock_session = MagicMock()
    mock_result = MagicMock()
    created_at = datetime.now(timezone.utc) - timedelta(
        seconds=auth.OTP_EXPIRY_SECONDS + 10
    )
    mock_result.fetchone.return_value = ("333333", created_at, 2)
    mock_session.execute.return_value = mock_result
    mock_get_db.return_value.__enter__.return_value = mock_session
    otp = auth.request_otp(EMAIL)
    assert otp == "222222"
    assert mock_session.execute.call_count == 2  # SELECT + UPDATE


@patch("signi_email_otp.auth.get_db")
@patch("signi_email_otp.auth.random.randint")
def test_request_otp_rate_limit(mock_randint, mock_get_db):
    mock_randint.return_value = 444444

    mock_session = MagicMock()
    mock_result = MagicMock()
    created_at = datetime.now(timezone.utc) - timedelta(seconds=10)
    mock_result.fetchone.return_value = ("444444", created_at, 0)
    mock_session.execute.return_value = mock_result
    mock_get_db.return_value.__enter__.return_value = mock_session

    with pytest.raises(RateLimitOTPExceededException):
        auth.request_otp(EMAIL)


@patch("signi_email_otp.auth.send_otp_email")
@patch("signi_email_otp.auth.request_otp")
def test_request_otp_and_send_email(mock_request_otp, mock_send_otp_email):
    mock_request_otp.return_value = "999999"
    auth.request_otp_and_send_email(EMAIL)
    mock_request_otp.assert_called_once_with(EMAIL)
    mock_send_otp_email.assert_called_once_with(EMAIL, "999999")
