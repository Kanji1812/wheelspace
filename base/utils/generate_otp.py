import random

def generate_otp():
    """Generate a 4-digit numeric OTP as an integer."""
    return random.randint(1000, 9999)

