from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.api.views import (AccountVerification, LoginView, RegisterView,ResendOtp,RequestPasswordResetAPIView,ConfirmPasswordResetAPIView,CustomerOnlyView)
urlpatterns = [
    # # JWT auth endpoints
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/verification/", AccountVerification.as_view(), name="verification"),
    path('auth/resend-otp/',ResendOtp.as_view(), name="resend_otp"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path('password-reset/request/', RequestPasswordResetAPIView.as_view(), name='request-password-reset'),
    path('password-reset/confirm/', ConfirmPasswordResetAPIView.as_view(), name='confirm-password-reset'),

    # test only 
    # path("CustomerOnlyView/", CustomerOnlyView.as_view(), name="CustomerOnlyView")
]
