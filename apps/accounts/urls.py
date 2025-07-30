from django.urls import path
from apps.accounts.views import (
    UserRegisterView,
    UserEmailVerificationView,
    UserResendVerificationEmailView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserChangePasswordView,
    UserSendResetPasswordEmailView,
    UserResetPasswordView,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("change-password/", UserChangePasswordView.as_view(), name="change-password"),
    path(
        "send-reset-password-email/",
        UserSendResetPasswordEmailView.as_view(),
        name="send-reset-password-email",
    ),
    path(
        "reset-password/<uid>/<token>/",
        UserResetPasswordView.as_view(),
        name="reset-password",
    ),
    path(
        "verify-email/<uid>/<token>/",
        UserEmailVerificationView.as_view(),
        name="verify-email",
    ),
    path(
        "resend-verification-email/",
        UserResendVerificationEmailView.as_view(),
        name="resend-verification-email",
    ),
]
