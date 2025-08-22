from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from base.utils.pagination import DefaultPagination
from rest_framework import status, viewsets, permissions,filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from users.models import Customer, User
from users.api.serializers import AdminSerializer, OwnerSerializer, RegisterSerializer  

from base.utils.sms_message import send_sms
from base.utils.standardized_response import api_response
from base.utils.generate_otp import generate_otp
from base.utils.permissions import IsCustomer, IsOwner, IsAdmin, IsOwnerOrIsAdmin
from vehicles.models import VehicleType

class RegisterView(APIView):
    """
    Register a new user.

    Creates a new user account with the provided data, then sends an OTP for verification
    via SMS and email.

    Responses:
        201 Created: User registered successfully.
        400 Bad Request: Invalid data or registration failed.
    """
    def post(self, request):
        """
        Handle user registration.

        Accepts:
        - full_name: str
        - email: str
        - phone_number: str
        - password: str
        - user_type: str

        Returns:
        - 201 with user data and success message on success.
        - 400 with error details if input is invalid.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            context = {
                "email": user.email,
                "user_name": user.full_name,
                "code": user.otp
            }

            # Send SMS
            # send_sms(user.phone_number, 'verification', code=user.otp)

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
                success=True,
                message=f"{user.user_type} registered successfully!",
                data={
                    # 'email': user.email,
                    # 'user_type': user.user_type,
                    # 'full_name':user.full_name,
                },
                status=status.HTTP_201_CREATED
            )

        # If serializer is not valid
        return api_response(
            success=False,
            message="Registration failed",
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class AccountVerification(APIView):
    """
    Verify user account using OTP.

    This endpoint checks if the provided OTP matches the one sent to the user’s email.

    Responses:
        200 OK: Account verified successfully.
        400 Bad Request: Missing/invalid email or OTP.
        404 Not Found: User not found.
    """
    def post(self, request):
        """
        POST method to verify OTP and activate the user's account.

        Accepts:
        - email: str
        - otp: str

        Returns:
        - 200 with access and refresh tokens if OTP is valid.
        - 400 if OTP is incorrect or missing.
        - 404 if user not found.
        """
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email:
            return api_response(message="Email cannot be empty.", status=status.HTTP_400_BAD_REQUEST,success=False)

        if len(email) < 6:
            return api_response(message="Enter Valid Email", status=status.HTTP_400_BAD_REQUEST,success=False)

        if not otp or len(str(otp)) < 4:
            return api_response(message="Enter Valid OTP", status=status.HTTP_400_BAD_REQUEST,success=False)

        user = User.objects.filter(email=email).first()
        if not user:
            return api_response(message="User not found", status=status.HTTP_404_NOT_FOUND,success=False)

        if str(user.otp) != str(otp):
            return api_response(message="Incorrect OTP", status=status.HTTP_400_BAD_REQUEST,success=False)
        user.otp = None
        user.is_verified = True
        user.save()
        refresh = RefreshToken.for_user(user)

        return api_response(
            success=True,
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
    """
    User login endpoint.

    Authenticates user with email and password and returns JWT tokens if the user is verified.

    Responses:
        200 OK: Login successful.
        400 Bad Request: Invalid credentials.
        403 Forbidden: User not verified.
    """
    # permission_classes = [AllowAny]

    def post(self, request):
        """
        POST method to log in the user.

        Accepts:
        - email: str
        - password: str

        Returns:
        - 200 with access and refresh JWT tokens if credentials and verification are valid.
        - 400 if credentials are invalid.
        - 403 if user is not verified.
        """
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)

        if user is not None:
            if not user.is_verified:
                return api_response(
                    success=False,
                    message="Account is not verified. Please verify your email or contact support.",
                    status=status.HTTP_403_FORBIDDEN
                )

            refresh = RefreshToken.for_user(user)
            return api_response(
                success=True,
                message="Login successful",
                status=status.HTTP_200_OK,
                data={
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user.user_type,
                    'name': user.full_name,
                }
            )

        return api_response(
            success=False,
            message="Invalid credentials",
            status=status.HTTP_400_BAD_REQUEST
        )

class ResendOtp(APIView):
    """
    Resend OTP to the user.

    Sends a new OTP via SMS and email to the registered user.

    Responses:
        200 OK: OTP sent.
        400 Bad Request: Email is missing.
        404 Not Found: User not found.
    """

    def post(self, request):
        """
        POST method to resend OTP.

        Accepts:
        - email: str

        Returns:
        - 200 if OTP is resent.
        - 400 if email is missing.
        - 404 if user does not exist.
        """
        email = request.data.get('email')

        if not email:
            return api_response(message="Email is required", status=status.HTTP_400_BAD_REQUEST,success=False)

        user = User.objects.filter(email=email).first()
        if not user:
            return api_response(message="User not found", status=status.HTTP_404_NOT_FOUND,success=False)

        # Generate new OTP (optional)
        new_otp = generate_otp()
        user.otp = new_otp
        user.save()

        # Send SMS
        # send_sms(user.phone_number, 'verification', code=new_otp)

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
            success=True,
            message="OTP resent successfully",
            data={"email": user.email},
            status=status.HTTP_200_OK
        )



class RequestPasswordResetAPIView(APIView):
    """
    Request password reset via OTP.

    Sends a password reset OTP to the user's registered email.

    Responses:
        200 OK: OTP sent for password reset.
        400 Bad Request: Missing email.
        404 Not Found: User not found.
    """
    def post(self, request):
        """
        POST method to initiate password reset.

        Accepts:
        - email: str

        Returns:
        - 200 if OTP is sent successfully.
        - 400 if email is missing.
        - 404 if user does not exist.
        """
        email = request.data.get('email')
        if not email:
            return api_response(message="Email is required", status=status.HTTP_400_BAD_REQUEST,success=False)

        user = User.objects.filter(email=email).first()
        if not user:
            return api_response(message="User not found", status=status.HTTP_404_NOT_FOUND,success=False)

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

        return api_response(message="OTP sent for password reset", data={"email": user.email}, status=status.HTTP_200_OK,success=True)


class ConfirmPasswordResetAPIView(APIView):
    """
    Confirm password reset using OTP.

    Verifies the OTP and sets the new password for the user.

    Responses:
        200 OK: Password reset successfully.
        400 Bad Request: Missing fields or invalid OTP.
        404 Not Found: User not found.
    """
    def post(self, request):
        """
        POST method to confirm password reset.

        Accepts:
        - email: str
        - otp: str
        - new_password: str

        Returns:
        - 200 if password is reset successfully.
        - 400 if any input is missing or OTP is invalid.
        - 404 if user does not exist.
        """
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return api_response(message="Email, OTP, and new password are required", status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return api_response(message="User not found", status=status.HTTP_404_NOT_FOUND)

        if str(user.otp) != str(otp):
            return api_response(message="Invalid OTP", status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.otp = None  
        user.save()

        return api_response(message="Password reset successfully", status=status.HTTP_200_OK)


class AdminViewSet(viewsets.ModelViewSet):
    serializer_class = AdminSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['age', 'user_type']
    search_fields = ['full_name', 'email', 'phone_number', 'address']
    ordering_fields = ['full_name', 'email', 'age']
    ordering = ['full_name']
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated, IsAdmin]  # enable this later

    def get_queryset(self):
        return User.objects.filter(user_type=User.Admin)

    def get_paginated_response(self, data):
        return api_response(
            success=True,
            message="Admin users fetched successfully!",
            data={
                "count": self.paginator.page.paginator.count,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "results": data,
            },
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return api_response(
                success=True,
                message="Admin user created successfully!",
                data=[serializer.data],
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return api_response(
                success=False,
                message="Validation Error",
                data=e.detail,
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Admin users fetched successfully!",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Admin user retrieved successfully!",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return api_response(
                success=True,
                message="Admin user updated successfully!",
                data=[serializer.data],   # wrap in list to match your format
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return api_response(
                success=False,
                message="Validation Error",
                data=e.detail,  # serializer validation errors
                status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return api_response(
            success=True,
            message="Admin user deleted successfully!",
            data={},
            status=status.HTTP_204_NO_CONTENT
        )

class OwnerViewSet(viewsets.ModelViewSet):
    serializer_class = OwnerSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['age','email', 'phone_number', 'address']
    search_fields = ['full_name', 'email', 'phone_number', 'address']
    ordering_fields = ['full_name', 'email', 'age','phone_number']
    ordering = ['full_name']
    # permission_classes = [AllowAny]
    permission_classes = [IsAuthenticated, IsOwnerOrIsAdmin]  
    def get_queryset(self):
        return User.objects.filter(user_type=User.ParkingOwner)

    def get_paginated_response(self, data):
        return api_response(
            success=True,
            message="Owner users fetched successfully!",
            data={
                "count": self.paginator.page.paginator.count,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "results": data,
            },
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return api_response(
                success=True,
                message="Owner user created successfully!",
                data=[serializer.data],
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return api_response(
                success=False,
                message="Validation Error",
                data=e.detail,
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Owner users fetched successfully!",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Owner user retrieved successfully!",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return api_response(
                success=True,
                message="Owner user updated successfully!",
                data=[serializer.data],
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return api_response(
                success=False,
                message="Validation Error",
                data=e.detail,
                status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return api_response(
            success=True,
            message="Owner user deleted successfully!",
            data={},
            status=status.HTTP_204_NO_CONTENT
        )

class UserViewSet(viewsets.ModelViewSet):
    """
    Single CRUD endpoint for both Owner and Customer users.
    - Owner: Only User object is handled.
    - Customer: User + Customer profile (vehicle type).
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    pagination_class = DefaultPagination

    # def get_permissions(self):
    #     if self.action in ["create"]:
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Handles user + (if customer) customer profile creation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": f"{user.user_type.capitalize()} registered successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """Update user and related customer if needed"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Update Customer vehicle type if user_type is customer
        if user.user_type == User.Customer and "vehicle_type" in request.data:
            vehicle_tobj = VehicleType.objects.get(id=request.data["vehicle_type"])
            Customer.objects.update_or_create(
                user=user, defaults={"vehicle_type": vehicle_tobj}
            )

        return Response(
            {"message": f"{user.user_type.capitalize()} updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """Delete user and cascade delete customer if exists"""
        instance = self.get_object()
        user_type = instance.user_type

        if user_type == User.Customer:
            Customer.objects.filter(user=instance).delete()

        instance.delete()
        return Response(
            {"message": f"{user_type.capitalize()} deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )