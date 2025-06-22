import os
from signi_email_otp.core import logger


def get_env(key, default=None):
    value = os.environ.get(key, default)
    if value is not None:
        if key in os.environ:
            logger.info(f"Environment variable {key} found: {value}")
        else:
            logger.warning(
                f"Environment variable {key} not found, using default: {default}"
            )
        return value
    raise KeyError(f"{key} not found in environment")


# OTP expiration in seconds
OTP_EXPIRY_SECONDS = get_env("OTP_EXPIRY_SECONDS", 300)

# JWT token expiration in seconds (default 7 days)
JWT_EXPIRY_SECONDS = get_env("JWT_EXPIRY_SECONDS", 604700)
# JWT secret key
JWT_SECRET = get_env("JWT_SECRET", "changeme")
JWT_ALGORITHM = get_env("JWT_ALGORITHM", "changeme")


# Email sending (for mock SMTP, etc.)
SMTP_HOST = get_env("SMTP_HOST", "localhost")
SMTP_PORT = get_env("SMTP_PORT", 25)
SMTP_FROM_EMAIL = get_env("SMTP_FROM_EMAIL", "test@test.com")
SMTP_FROM_PASSWORD = get_env("SMTP_PASSWORD", "changeme")

# Database configuration
DB_URL = get_env("DB_URL", "postgresql+psycopg2://otpuser:otppass@db:5432/otpdb")
MAX_CONN = int(get_env("DB_POOL_MAX_CONN", 5))


# Logging configuration
LOG_LEVEL = get_env("LOG_LEVEL", "INFO").upper()
LOG_FILE = get_env("LOG_FILE", "signi_email_otp.log")
