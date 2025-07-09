from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from base.utils.send_email import send_emails 
from base.utils.sms_message import send_sms
from users.models import User
from .serializers import RegisterSerializer
from django.template.loader import render_to_string
from rest_framework import viewsets
from rest_framework.decorators import action

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    @action(detail=False,method=["post"])
    def my_demo(self,request):
        print("kanji")
        
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            context = {
                "email":user.email, 
                "user_name":user.username,
                "code":user.otp
            }
            is_message_send = send_sms(User.phone_number, 'verification', code=User.otp)
            html_content = render_to_string('email_template/demo_email_body.html', context)
            is_email_send = send_emails(send_to=user.email,subject="Verify your email address",html=html_content)
            if is_email_send:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'email':user.email,
                    'user_type': user.user_type,
                    'message': 'User registered successfully!'
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountVerification(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        if not email:
            return Response({"message": "Email cannot be empty."}, status=400)
        
        if len(email) < 6:
            return Response({"message": "Enter Valid Email"}, status=status.HTTP_400_BAD_REQUEST)

        if not otp or len(str(otp)) < 4:
            return Response({"message": "Enter Valid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.otp != otp:
            return Response({"message": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)

        # If OTP is correct
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'name': user.username,
            'user_type': user.user_type,
            'message': 'account verification successfully!'
        }, status=status.HTTP_200_OK)
        
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')  
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_type': user.user_type
            })
        else:
            return Response({"error": "Invalid credentials"}, status=400)
