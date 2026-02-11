import aiosmtplib
from email.message import EmailMessage
from app.config import get_settings


async def send_email(to_address: str, subject: str, body: str) -> str:
    """Send an email via SMTP.

    Args:
        to_address: Recipient email address.
        subject: Email subject line.
        body: Email body text (plain text).
    """
    settings = get_settings()

    if not settings.smtp_host:
        return "Error: Email sending is not configured. SMTP settings are missing."

    try:
        msg = EmailMessage()
        msg["From"] = settings.smtp_from_address
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.set_content(body)

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            use_tls=settings.smtp_use_tls,
            timeout=30,
        )
        return f"Email sent successfully to {to_address} with subject '{subject}'."
    except Exception as e:
        return f"Failed to send email: {str(e)}"
