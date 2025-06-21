class signiEmailOTPException(Exception):
    """Base exception for signi_email_otp errors."""

    pass


class RateLimitOTPExceededException(signiEmailOTPException):
    """Raised when the rate limit for OTP requests is exceeded."""

    def __init__(self, message="Rate limit exceeded. Please try again later."):
        super().__init__(message)


class InvalidOTPException(signiEmailOTPException):
    """Raised when an invalid OTP is provided."""

    def __init__(self, message="Invalid OTP provided. Please try again."):
        super().__init__(message)


class OTPExpiredException(signiEmailOTPException):
    """Raised when an OTP has expired."""

    def __init__(self, message="OTP has expired. Please request a new one."):
        super().__init__(message)


class OTPNotFoundException(signiEmailOTPException):
    """Raised when an OTP is not found in the database."""

    def __init__(self, message="OTP not found. Please request a new one."):
        super().__init__(message)
