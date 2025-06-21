import jwt
import pytest
from signi_email_otp.jwt_utils import generate_jwt, decode_jwt

SECRET = "testsecret"
ALGORITHM = "HS256"
EXPIRY_SECONDS = 2


def test_generate_and_decode_jwt():
    email: str = "test@test.com"
    token, exp_dt = generate_jwt(email, SECRET, ALGORITHM, EXPIRY_SECONDS)
    assert isinstance(token, str)
    assert exp_dt is not None
    decoded = decode_jwt(token, SECRET, ALGORITHM)
    assert decoded["email"] == "test@test.com"
    assert "exp" in decoded


def test_decode_jwt_invalid_signature():
    email: str = "test@test.com"
    token, _ = generate_jwt(email, SECRET, ALGORITHM, EXPIRY_SECONDS)
    with pytest.raises(jwt.exceptions.InvalidSignatureError):
        decode_jwt(token, "wrongsecret", ALGORITHM)


def test_decode_jwt_expired():
    import time

    payload = {"user_id": 123}
    token, _ = generate_jwt(payload, SECRET, ALGORITHM, 1)
    time.sleep(2)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_jwt(token, SECRET, ALGORITHM)
