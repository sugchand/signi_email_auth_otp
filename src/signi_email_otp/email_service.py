import smtplib
from email.mime.text import MIMEText
from .core import logger


def send_otp_email(
    smtp_host: str,
    smtp_port: int,
    email_from: str,
    email_password: str,
    email_to: str,
    subject: str,
    body: str,
) -> str | None:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(email_from, email_password)
            server.sendmail(email_from, [email_to], msg.as_string())
            logger.info(
                (
                    f"Email sent successfully to {email_to} "
                    f"with subject '{subject}'"
                )
            )
            return None
    except Exception as e:
        logger.error(
            f"Failed to send email to {email_to} with subject '{subject}': {e}"
        )
        raise
