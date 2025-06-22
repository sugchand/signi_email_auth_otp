import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_otp_flow():
    email = "integration@example.com"
    # Request OTP
    resp = requests.post(f"{BASE_URL}/otp/request", json={"email": email})
    assert resp.status_code == 200
    otp = resp.json()["otp"]
    assert otp.isdigit() and len(otp) == 6

    # Verify OTP
    refresh_token = requests.post(
        f"{BASE_URL}/otp/verify",
        json={"email": email, "otp": otp}
    )
    assert refresh_token.status_code == 200

    # lets call again to ensure it works with the same OTP
    resp = requests.post(f"{BASE_URL}/otp/request", json={"email": email})
    assert resp.status_code == 200
    otp = resp.json()["otp"]
    assert otp.isdigit() and len(otp) == 6

    refresh_token2 = requests.post(
        f"{BASE_URL}/otp/verify",
        json={"email": email, "otp": otp}
    )
    assert refresh_token2.status_code == 200
    assert refresh_token2.json() == refresh_token.json()
