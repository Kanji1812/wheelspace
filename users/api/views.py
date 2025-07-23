from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from base.utils.sms_message import send_sms
from users.models import User
from .serializers import RegisterSerializer
from django.template.loader import render_to_string
from rest_framework import viewsets
from rest_framework.decorators import action
from django.core.mail import EmailMessage
from base.utils.standardized_response import api_response
from base.utils.generate_otp import generate_otp
from django.contrib.auth.hashers import make_password

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            context = {
                "email": user.email,
                "user_name": user.full_name,
                "code": user.otp
            }

            # Send SMS
            send_sms(user.phone_number, 'verification', code=user.otp)

            # Render and send email
            html_content = render_to_string('email_template/demo_email_body.html', context)
            email = EmailMessage(
                subject="Verify your email address",
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )
            email.content_subtype = "html"

            try:
                email.send(fail_silently=False)
            except Exception as e:
                print(f"Error sending email: {e}")

            refresh = RefreshToken.for_user(user)

            return api_response(
                message=f"{user.user_type} registered successfully!",
                data={
                    'email': user.email,
                    'user_type': user.user_type,
                    'full_name':user.full_name,
                },
                status=status.HTTP_201_CREATED
            )

        # If serializer is not valid
        return api_response(
            message="Registration failed",
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class AccountVerification(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email:
            return api_response(message="Email cannot be empty.", status=status.HTTP_400_BAD_REQUEST)

        if len(email) < 6:
            return api_response(message="Enter Valid Email", status=status.HTTP_400_BAD_REQUEST)

        if not otp or len(str(otp)) < 4:
            return api_response(message="Enter Valid OTP", status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return api_response(message="User not found", status=status.HTTP_404_NOT_FOUND)

        if str(user.otp) != str(otp):
            return api_response(message="Incorrect OTP", status=status.HTTP_400_BAD_REQUEST)
        user.otp = None
        user.is_verified = True
        user.save()
        refresh = RefreshToken.for_user(user)

        return api_response(
            message="Account verified successfully!",
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'name': user.full_name,
                'user_type': user.user_type
            },
            status=status.HTTP_200_OK
        )
    


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')  
        password = request.data.get('password')

        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return api_response(
                message="Login successful",
                data={
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user.user_type,
                    'name':user.full_name,
                },
                status=status.HTTP_200_OK
            )
        else:
            return api_response(message="Invalid credentials", status=status.HTTP_400_BAD_REQUEST)


class ResendOtp(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return api_response(message="Email is required", status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return api_response(message="User not found", status=status.HTTP_404_NOT_FOUND)

        # Generate new OTP (optional)
        new_otp = generate_otp()
        user.otp = new_otp
        user.save()

        # Send SMS
        send_sms(user.phone_number, 'verification', code=new_otp)

        # Send Email
        context = {
            "email": user.email,
            "user_name": user.full_name,
            "code": new_otp
        }
        html_content = render_to_string('email_template/demo_email_body.html', context)

        email_obj = EmailMessage(
            subject="Your OTP code",
            body=html_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email_obj.content_subtype = "html"

        try:
            email_obj.send(fail_silently=False)
        except Exception as e:
            print(f"Error sending email: {e}")

        return api_response(
            message="OTP resent successfully",
            data={"email": user.email},
            status=status.HTTP_200_OK
        )



class RequestPasswordResetAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return api_response(message="Email is required", status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return api_response(message="User not found", status=status.HTTP_404_NOT_FOUND)

        otp = generate_otp()
        user.otp = otp
        user.save()

        # Send SMS
        # send_sms(user.phone_number, 'reset', code=otp)

        # Send Email
        context = {
            "email": user.email,
            "user_name": user.full_name,
            "otp_code": otp
        }
        html_content = render_to_string('email_template/password_reset_otp.html', context)

        email_msg = EmailMessage(
            subject="Reset Your Password - OTP",
            body=html_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email_msg.content_subtype = "html"

        try:
            email_msg.send()
        except Exception as e:
            print(f"Email error: {e}")

        return api_response(message="OTP sent for password reset", data={"email": user.email}, status=200)


class ConfirmPasswordResetAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return api_response(message="Email, OTP, and new password are required", status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return api_response(message="User not found", status=404)

        if str(user.otp) != str(otp):
            return api_response(message="Invalid OTP", status=400)

        user.password = make_password(new_password)
        user.otp = None  
        user.save()

        return api_response(message="Password reset successfully", status=200)