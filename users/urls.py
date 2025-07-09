from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.api.views import AccountVerification, LoginView, RegisterView
urlpatterns = [
    # JWT auth endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("register/", RegisterView.as_view(), name="register"),
    path("api/verification/", AccountVerification.as_view(), name="verification"),
    path("api/login/", LoginView.as_view(), name="verification"),

]
