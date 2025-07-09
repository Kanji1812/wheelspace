from twilio.rest import Client
from django.conf import settings

SMS_TEMPLATES = {
    "welcome": "Welcome to Wheel Space, {name}! We're excited to have you on board.",
    "verification": "Your Wheel Space verification code is: {code}",
    "offer": "Special Offer from Wheel Space! {offer_details} Hurry, limited time only!"
}

def send_sms(to_number, template_type, **kwargs):
    """
    Sends SMS using Twilio with a selected template.

    :param to_number: Recipient phone number (e.g., +917227807493)
    :param template_type: One of 'welcome', 'verification', 'offer'
    :param kwargs: Template variables (e.g., name='John', code='123456')
    """
    account_sid = settings.ACCOUNT_SID
    auth_token = settings.AUTH_TOKEN
    client = Client(account_sid, auth_token)

    if template_type not in SMS_TEMPLATES:
        raise ValueError(f"Unknown template type: {template_type}")

    body = SMS_TEMPLATES[template_type].format(**kwargs)

    try:
        message = client.messages.create(
            from_='+12172698178', 
            body=body,
            to=f"+91{to_number}"
        )
        print(f"Message sent. SID: {message.sid}")
        return message.sid
    except Exception as e:
        print(f"Error sending message: {e}")
        return None
