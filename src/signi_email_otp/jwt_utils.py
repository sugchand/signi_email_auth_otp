import jwt
import time
from datetime import datetime


def generate_jwt(
    email: str, secret: str, algorithm: str, expiry_seconds: int
) -> tuple[str, datetime]:
    exp_timestamp = int(time.time()) + expiry_seconds
    payload = {"email": email, "exp": exp_timestamp}
    token = jwt.encode(payload, secret, algorithm=algorithm)
    return token, datetime.fromtimestamp(exp_timestamp)


def decode_jwt(token: str, secret: str, algorithm: str) -> dict:
    return jwt.decode(token, secret, algorithms=[algorithm])
