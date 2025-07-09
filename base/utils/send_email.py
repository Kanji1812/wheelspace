# utils/email.py
import resend
from django.core.mail import send_mail
# from django.conf import settings

# resend.api_key = settings.RESEND_API_KEY

def send_emails(send_to, subject, html):
    try:
        response = send_mail(
                subject,
                html,
                "parthlanzariya123@gmail.com",
                [send_to],
                fail_silently=False,
            )
        return response
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
