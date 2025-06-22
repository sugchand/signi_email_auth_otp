import random
from datetime import datetime, timezone
from .email_service import send_otp_email
from .jwt_utils import generate_jwt
from .config import (
    OTP_EXPIRY_SECONDS,
    JWT_SECRET,
    JWT_EXPIRY_SECONDS,
    JWT_ALGORITHM,
)
from .db import get_db
from .core import logger
from .exception import (
    RateLimitOTPExceededException,
    OTPNotFoundException,
    InvalidOTPException,
    OTPExpiredException,
)
from sqlalchemy import text


def request_otp(email) -> str:
    logger.info(f"Requesting OTP for email: {email}")
    otp: str = ""
    with get_db() as session:
        logger.debug(f"Requesting OTP for email: {email} and db session: {JWT_SECRET}")
        # Check existing valid OTP
        result = session.execute(
            text(
                """
                SELECT otp_code, created_at, attempts_left
                FROM otp
                WHERE email = %s
                """
            ),
            {"email": email},
        )
        row = result.fetchone()

        if row:
            existing_otp, created_at, attempts_left = row
            otp_age = (datetime.now(timezone.utc) - created_at).total_seconds()
            if otp_age < OTP_EXPIRY_SECONDS:
                if attempts_left > 0:
                    session.execute(
                        text(
                            """
                            UPDATE otp SET attempts_left = attempts_left - 1
                            WHERE email = %s
                            """
                        ),
                        {"email": email},
                    )
                    logger.info(
                        (
                            (
                                f"Reusing existing OTP for {email}, "
                                f"age: {otp_age} seconds"
                            )
                        )
                    )
                    otp = existing_otp
                else:
                    logger.warning(
                        (
                            f"OTP for {email} has no attempts left, "
                            "rate limiting applied."
                        )
                    )
                    raise RateLimitOTPExceededException(
                        "Maximum attempts exceeded. Please try again later."
                    )
            else:
                logger.info(f"Existing OTP for {email} expired, generating new OTP.")
                otp = str(random.randint(100000, 999999))
                session.execute(
                    text(
                        """
                        UPDATE otp SET otp_code = %s, created_at = NOW()
                        WHERE email = %s
                        """
                    ),
                    {"otp_code": otp, "email": email},
                )
        else:
            logger.debug(f"No existing OTP found for {email}, " "generating new OTP.")
            otp = str(random.randint(100000, 999999))
            session.execute(
                text(
                    """
                    INSERT INTO otp (email, otp, created_at)
                    VALUES (%s, %s, NOW())
                    """,
                ),
                {"email": email, "otp_code": otp},
            )
            logger.info(f"Generated new OTP for {email}")
    return otp


def request_otp_and_send_email(email):
    """
    Request an OTP for the given email and send it via email.
    If an existing valid OTP exists, it will be reused.
    """
    otp = request_otp(email)
    send_otp_email(email, otp)


def verify_otp(email, otp):
    with get_db() as session:
        # Cleanup expired OTPs
        session.execute(
            text(
                """
                DELETE FROM otp
                WHERE created_at < NOW() - INTERVAL :interval
                """
            ),
            {"interval": f"{OTP_EXPIRY_SECONDS} seconds"},
        )

        # Fetch valid OTP
        session.execute(
            text(
                """
                SELECT otp_code, created_at FROM otp WHERE email = %s
                """
            ),
            {"email": email},
        )
        row = session.fetchone()

        if not row:
            logger.warning(f"OTP not found for email: {email}")
            raise OTPNotFoundException("OTP not found for this email")
        db_otp, created_at = row

        if db_otp != otp:
            logger.warning(f"Invalid OTP for email: {email}")
            raise InvalidOTPException("Invalid OTP provided.")

        otp_age = (datetime.now(timezone.utc) - created_at).total_seconds()
        if otp_age > OTP_EXPIRY_SECONDS:
            logger.warning(f"OTP expired for email: {email}")
            raise OTPExpiredException("OTP has expired")

        # Delete the OTP after successful verification
        session.execute(
            text(
                """
                DELETE FROM otp WHERE email = %s
                """
            ),
            {"email": email},
        )
        # Generate and store JWT
        token, exp_time = generate_jwt(
            email, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_SECONDS
        )
        session.execute(
            text(
                """
                    INSERT INTO refresh_tokens
                    (refresh_token, email, created_at, expires_at)
                    VALUES (%s, %s, NOW(), %s)
                    ON CONFLICT (email) DO UPDATE SET
                        token = token,
                        created_at = NOW(),
                        expires_at = EXCLUDED.expires_at
                    """
            ),
            {"refresh_token": token, "email": email, "expires_at": exp_time},
        )

    return token
