from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import (
    RefreshToken,
    TokenError,
)

# Password reset
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.utils.encoding import (
    smart_str,
    force_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)

from apps.accounts.utils import Util

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["email", "name", "password", "password2"]
        extra_kwargs = {
            "email": {"required": True},
            "name": {"required": True},
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    # Verify via email
    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        user.is_active = False
        user.save()

        # Send verification email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"http://localhost:3000/api/users/verify/{uid}/{token}/"

        body = f"Hi {user.name},\n\nClick to verify your email:\n{activation_link}"
        data = {
            "subject": "Verify your email",
            "body": body,
            "to_email": user.email,
        }

        try:
            Util.send_email(data)
        except Exception as e:
            print("Verification email error:", e)

        return user


class UserResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate_email(self, value):
        # Check if unverified user exists
        self.user = User.objects.filter(email=value, is_active=False).first()
        if not self.user:
            # Don't reveal whether email exists for security
            raise ValidationError(
                "If this email exists and is unverified, a new verification link has been sent"
            )
        return value

    def save(self):
        user = self.user

        # Reset the verification timeout
        user.updated_at = timezone.now()
        user.save()

        # Generate new token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Create verification link
        activation_link = f"http://localhost:3000/api/users/verify/{uid}/{token}/"
        expiration_minutes = settings.EMAIL_VERIFICATION_TIMEOUT // 60

        # Prepare email
        data = {
            "subject": "Verify your email",
            "body": f"""
                Hi {user.name},
                
                Click to verify your email (expires in {expiration_minutes} minutes):
                {activation_link}
                
                If you didn't request this, please ignore this email.
                """,
            "to_email": user.email,
        }

        # Send email using your Util class
        try:
            Util.send_email(data)
        except Exception as e:
            # Log error properly in production
            print(f"Failed to send verification email: {str(e)}")
            # Don't raise error to avoid revealing email status


class UserEmailVerificationSerializer(serializers.Serializer):

    def validate(self, attrs):
        uid = self.context.get("uid")
        token = self.context.get("token")
        try:
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)

            # Add this check for token expiration
            token_age = (timezone.now() - user.updated_at).total_seconds()
            if token_age > settings.EMAIL_VERIFICATION_TIMEOUT:
                raise serializers.ValidationError("Verification link has expired")

        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError("Invalid verification link.")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token.")

        if user.is_active:
            raise serializers.ValidationError("Email already verified.")

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.is_active = True
        user.save()
        return user


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"msg": "User does not exist."})

        if not user.check_password(password):
            raise serializers.ValidationError({"msg": "Invalid email or password."})

        if not user.is_active:
            raise serializers.ValidationError(
                {"msg": "Please verify your email to activate your account."}
            )

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email"]


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["password", "password2"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        user = self.context.get("user")
        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        # Check if new password is same as old password
        if user.check_password(password):
            raise serializers.ValidationError(
                "New password cannot be the same as the old password."
            )
        user.set_password(password)
        user.save()
        return attrs


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    default_error_messages = {
        "bad_token": "Token is expired or invalid",
        "token_missing": "Refresh token is required",
    }

    def validate(self, attrs):
        if not attrs.get("refresh"):
            self.fail("token_missing")
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except (TokenError, AttributeError, TypeError):
            self.fail("bad_token")


class UserSendResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        # user = User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        if not user:
            raise serializers.ValidationError("User does not exist.")
        if not user.is_active:
            raise serializers.ValidationError(
                "User is not not verified. Please verify your email first."
            )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        activation_link = f"http://localhost:3000/api/users/reset/{uid}/{token}/"
        expiration_minutes = settings.PASSWORD_RESET_TIMEOUT // 60

        # Prepare email
        data = {
            "subject": "Reset your password",
            "body": f"""
                Hi {user.name},
                
                Click link to reset your password: (expires in {expiration_minutes} minutes):
                {activation_link}
                
                If you didn't request this, please ignore this email.
                """,
            "to_email": user.email,
        }

        # Send email using your Util class
        try:
            Util.send_email(data)
        except Exception as e:
            print("error sending mail:", e)

        return attrs


class UserResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["password", "password2"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            password2 = attrs.get("password2")
            uid = self.context.get("uid")
            token = self.context.get("token")
            id = smart_str(urlsafe_base64_decode(uid))
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid username or password.")
            if password != password2:
                raise serializers.ValidationError("Passwords do not match.")
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError(
                    "The reset token is invalid or expired."
                )
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("The reset token is invalid or expired.")
