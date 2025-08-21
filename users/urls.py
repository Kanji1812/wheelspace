from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from rest_framework.routers import DefaultRouter

from users.api.views import (
    AccountVerification,
    LoginView,
    RegisterView,
    ResendOtp,
    RequestPasswordResetAPIView,
    ConfirmPasswordResetAPIView,
    CustomerOnlyView,
    AdminViewSet,
    OwnerViewSet
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'admin', AdminViewSet, basename='admin')  # Registers /api/admin/
router.register(r'owners', OwnerViewSet, basename='owner')

# URL patterns
urlpatterns = [
    # JWT auth endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Uncommented for completeness
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Auth-related endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/verification/', AccountVerification.as_view(), name='verification'),
    path('auth/resend-otp/', ResendOtp.as_view(), name='resend_otp'),
    path('auth/login/', LoginView.as_view(), name='login'),
    
    # Password reset endpoints
    path('password-reset/request/', RequestPasswordResetAPIView.as_view(), name='request-password-reset'),
    path('password-reset/confirm/', ConfirmPasswordResetAPIView.as_view(), name='confirm-password-reset'),

    # Test endpoint (optional)
    # path('customer-only/', CustomerOnlyView.as_view(), name='customer-only'),
]

# Combine router URLs
urlpatterns += router.urls