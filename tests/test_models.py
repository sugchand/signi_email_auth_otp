from signi_email_otp.models import OTP, JWT, utcnow_timeaware
from datetime import datetime, timezone


def test_otp_model_fields():
    now = utcnow_timeaware()
    otp = OTP(
        email="user@example.com",
        otp_code="123456",
        created_at=now,
        used=False,
        attempts_left=3,
    )
    assert otp.email == "user@example.com"
    assert otp.otp_code == "123456"
    assert isinstance(otp.created_at, datetime)
    assert otp.created_at.tzinfo == timezone.utc
    assert otp.used is False
    assert otp.attempts_left == 3


def test_jwt_model_fields():
    now = utcnow_timeaware()
    jwt = JWT(
        email="user@example.com",
        refresh_token="sometoken",
        created_at=now,
        expires_at=now,
    )
    assert jwt.email == "user@example.com"
    assert jwt.refresh_token == "sometoken"
    assert isinstance(jwt.created_at, datetime)
    assert jwt.created_at.tzinfo == timezone.utc
    assert isinstance(jwt.expires_at, datetime)
    assert jwt.expires_at.tzinfo == timezone.utc


def test_utcnow_timeaware():
    now = utcnow_timeaware()
    assert isinstance(now, datetime)
    assert now.tzinfo == timezone.utc