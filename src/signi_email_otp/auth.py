import random
from datetime import datetime, timezone, timedelta
from .email_service import send_otp_email
from .jwt_utils import generate_jwt
from .config import (
    OTP_EXPIRY_SECONDS,
    JWT_SECRET,
    JWT_EXPIRY_SECONDS,
    JWT_ALGORITHM,
)
from .db import get_db
from .models import OTP, JWT
from .core import logger
from .exception import (
    RateLimitOTPExceededException,
    OTPNotFoundException,
    InvalidOTPException,
    OTPExpiredException,
)


def request_otp(email) -> str:
    logger.info(f"Requesting OTP for email: {email}")
    otp: str = ""
    with get_db() as session:
        logger.debug(f"Requesting OTP for email: {email} and db session: {JWT_SECRET}")
        # Check existing valid OTP
        otp_obj = session.query(OTP).filter_by(email=email).first()

        if otp_obj:
            existing_otp = otp_obj.otp_code
            created_at = otp_obj.created_at
            attempts_left = otp_obj.attempts_left
            otp_age = (datetime.now(timezone.utc) - created_at).total_seconds()
            if otp_age < OTP_EXPIRY_SECONDS:
                if attempts_left > 0:
                    otp_obj.attempts_left -= 1
                    session.add(otp_obj)
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
                otp_obj.otp_code = otp
                otp_obj.created_at = datetime.now(timezone.utc)
                otp_obj.attempts_left = 3
                session.add(otp_obj)
        else:
            logger.debug(f"No existing OTP found for {email}, " "generating new OTP.")
            otp = str(random.randint(100000, 999999))
            otp_obj = OTP(
                email=email,
                otp_code=otp,
                created_at=datetime.now(timezone.utc),
                attempts_left=3,
            )
            session.add(otp_obj)
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
        expiry_time = datetime.now(timezone.utc) - timedelta(seconds=OTP_EXPIRY_SECONDS)
        session.query(OTP).filter(OTP.created_at < expiry_time).delete(
            synchronize_session=False
        )

        otp_obj = session.query(OTP).filter_by(email=email).first()
        if not otp_obj:
            logger.warning(f"OTP not found for email: {email}")
            raise OTPNotFoundException("OTP not found for this email")
        db_otp = otp_obj.otp_code
        created_at = otp_obj.created_at

        if db_otp != otp:
            logger.warning(f"Invalid OTP for email: {email}")
            raise InvalidOTPException("Invalid OTP provided.")

        otp_age = (datetime.now(timezone.utc) - created_at).total_seconds()
        if otp_age > OTP_EXPIRY_SECONDS:
            logger.warning(f"OTP expired for email: {email}")
            raise OTPExpiredException("OTP has expired")

        # Delete the OTP after successful verification, to avoid reuse
        session.delete(otp_obj)

        # Lets first check for an existing JWT for the email
        # assume if user logged in from different device, we will reuse the JWT.
        jwt_obj = session.query(JWT).filter_by(email=email).first()
        if jwt_obj:
            logger.info(f"JWT already exists for {email}, reusing it.")
            token = jwt_obj.refresh_token
        else:
            logger.info(f"No JWT found for {email}, generating a new one.")
            # Generate and store JWT
            token, exp_time = generate_jwt(
                email, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_SECONDS
            )
            jwt_obj = JWT(
                email=email,
                refresh_token=token,
                created_at=datetime.now(timezone.utc),
                expires_at=exp_time,
            )
            session.add(jwt_obj)
    return token
