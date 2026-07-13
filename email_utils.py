import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(override=True)


EMAIL = os.getenv("EMAIL", "").strip()

# Gmail App Password मध्ये spaces असतील तर remove होतील
APP_PASSWORD = os.getenv("APP_PASSWORD", "").replace(" ", "").strip()


def send_otp(receiver_email, otp):

    if not EMAIL:
        print("Email Error: EMAIL is missing in .env")
        return False

    if not APP_PASSWORD:
        print("Email Error: APP_PASSWORD is missing in .env")
        return False

    try:

        message = MIMEMultipart()

        message["Subject"] = "AI Career Copilot - Password Reset OTP"
        message["From"] = EMAIL
        message["To"] = receiver_email

        body = f"""
Hello,

Your password reset OTP is: {otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.

Regards,
AI Career Copilot
"""

        message.attach(
            MIMEText(body, "plain", "utf-8")
        )

        with smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=30
        ) as server:

            server.ehlo()
            server.starttls()
            server.ehlo()

            server.login(
                EMAIL,
                APP_PASSWORD
            )

            server.sendmail(
                EMAIL,
                receiver_email,
                message.as_string()
            )

        print("OTP email sent successfully to:", receiver_email)

        return True

    except smtplib.SMTPAuthenticationError as e:

        print("Email Authentication Error:", e)

        return False

    except Exception as e:

        print("Email Error:", repr(e))

        return False