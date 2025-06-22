import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

from signi_email_otp import auth
from signi_email_otp.auth import RateLimitOTPExceededException
from signi_email_otp.models import OTP

EMAIL = "user@example.com"


@pytest.fixture
def mock_session():
    return MagicMock()


@patch("signi_email_otp.auth.get_db")
@patch("signi_email_otp.auth.random.randint")
def test_request_otp_new(mock_randint, mock_get_db):
    mock_randint.return_value = 123456
    mock_session = MagicMock()
    # Simulate no existing OTP
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    mock_get_db.return_value.__enter__.return_value = mock_session

    otp = auth.request_otp(EMAIL)
    assert otp == "123456"
    # Should add a new OTP object
    assert mock_session.add.called


@patch("signi_email_otp.auth.get_db")
@patch("signi_email_otp.auth.random.randint")
def test_request_otp_reuse_valid(mock_randint, mock_get_db):
    mock_randint.return_value = 654321
    mock_session = MagicMock()
    created_at = datetime.now(timezone.utc) - timedelta(seconds=10)
    otp_obj = OTP(
        email=EMAIL,
        otp_code="111111",
        created_at=created_at,
        used=False,
        attempts_left=2,
    )
    mock_session.query.return_value.filter_by.return_value.first.return_value = otp_obj
    mock_get_db.return_value.__enter__.return_value = mock_session

    otp = auth.request_otp(EMAIL)
    assert otp == "111111"
    # Should not add a new OTP object, just reuse


@patch("signi_email_otp.auth.get_db")
@patch("signi_email_otp.auth.random.randint")
def test_request_otp_expired(mock_randint, mock_get_db):
    mock_randint.return_value = 222222
    mock_session = MagicMock()
    created_at = datetime.now(timezone.utc) - timedelta(
        seconds=auth.OTP_EXPIRY_SECONDS + 10
    )
    otp_obj = OTP(
        email=EMAIL,
        otp_code="333333",
        created_at=created_at,
        used=False,
        attempts_left=2,
    )
    mock_session.query.return_value.filter_by.return_value.first.return_value = otp_obj
    mock_get_db.return_value.__enter__.return_value = mock_session

    otp = auth.request_otp(EMAIL)
    assert otp == "222222"
    # Should update the existing OTP object


@patch("signi_email_otp.auth.get_db")
@patch("signi_email_otp.auth.random.randint")
def test_request_otp_rate_limit(mock_randint, mock_get_db):
    mock_randint.return_value = 444444
    mock_session = MagicMock()
    created_at = datetime.now(timezone.utc) - timedelta(seconds=10)
    otp_obj = OTP(
        email=EMAIL,
        otp_code="444444",
        created_at=created_at,
        used=False,
        attempts_left=0,
    )
    mock_session.query.return_value.filter_by.return_value.first.return_value = otp_obj
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
