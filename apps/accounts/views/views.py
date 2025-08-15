from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from apps.accounts.serializers import (
    UserRegisterSerializer,
    UserEmailVerificationSerializer,
    UserResendVerificationEmailSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserProfileSerializer,
    UserChangePasswordSerializer,
    UserSendResetPasswordEmailSerializer,
    UserResetPasswordSerializer,
)
from apps.accounts.throttles import (
    RegisterRateThrottle,
    LoginRateThrottle,
    ResendVerificationRateThrottle,
    ChangePasswordRateThrottle,
    SendResetPasswordEmailThrottle,
    ResetPasswordRateThrottle,
    EmailVerificationRateThrottle,
    EmailVerificationAnonRateThrottle,
)

def get_tokens_for_user(user):
    """Returns refresh and access tokens for a user."""
    if not user.is_active:
        raise AuthenticationFailed(
            {
                "detail": "Account not verified",
                "code": "unverified_account",
                "resolution": "Please verify your email first",
            }
        )

    try:
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "token_type": "bearer",
            "expires_in": refresh.access_token.payload["exp"],
        }

    except Exception:
        raise AuthenticationFailed("Could not generate tokens")


class UserRegisterView(APIView):
    throttle_classes = [RegisterRateThrottle]

    @extend_schema(
        request=UserRegisterSerializer,
        responses=UserRegisterSerializer,
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # token = get_tokens_for_user(user)
        return Response(
            {
                "msg": "Registration successful. Please check your email for verification"
            },
            status=status.HTTP_201_CREATED,
        )


class UserResendVerificationEmailView(APIView):
    throttle_classes = [ResendVerificationRateThrottle]

    @extend_schema(
        request=UserResendVerificationEmailSerializer,
        responses=UserResendVerificationEmailSerializer,
    )
    def post(self, request):
        serializer = UserResendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"msg": "A new verification link has been sent to your email"},
            status=status.HTTP_200_OK,
        )


class UserEmailVerificationView(APIView):
    throttle_classes = [
        EmailVerificationRateThrottle,
        EmailVerificationAnonRateThrottle
    ]

    @extend_schema(
        request=UserEmailVerificationSerializer,
        responses=UserEmailVerificationSerializer,
    )
    def post(self, request, uid, token):
        serializer = UserEmailVerificationSerializer(
            data=request.data,
            context={"uid": uid, "token": token},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response(
            {
                "msg": "Email verified successfully. You are now logged in.",
                "token": token,
            },
            status=status.HTTP_200_OK,
        )


class UserLoginView(APIView):
    throttle_classes = [LoginRateThrottle]

    @extend_schema(
        request=UserLoginSerializer,
        responses=UserLoginSerializer,
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = get_tokens_for_user(user)
        return Response(
            {"msg": "Login successful", "token": token},
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserProfileSerializer,
        responses=UserProfileSerializer,
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePasswordView(APIView):
    throttle_classes = [ChangePasswordRateThrottle]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UserChangePasswordSerializer)
    def post(self, request):
        serializer = UserChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class UserLogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UserLogoutSerializer)
    def post(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSendResetPasswordEmailView(APIView):
    throttle_classes = [SendResetPasswordEmailThrottle]

    @extend_schema(request=UserSendResetPasswordEmailSerializer)
    def post(self, request):
        serializer = UserSendResetPasswordEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password reset email sent. Please check your email"},
            status=status.HTTP_200_OK,
        )


class UserResetPasswordView(APIView):
    throttle_classes = [ResetPasswordRateThrottle]

    @extend_schema(request=UserResetPasswordSerializer)
    def post(self, request, uid, token):
        serializer = UserResetPasswordSerializer(
            data=request.data,
            context={"uid": uid, "token": token},
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"msg": "Password reset successful"},
            status=status.HTTP_200_OK,
        )
